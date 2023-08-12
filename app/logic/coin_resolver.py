from app.db.database import Database
from app.services.coin_market_cap import CoinMarketCap
from app.services.crypto_compare import CryptoCompare
from app.services.time_service import TimeService, time_format
from app.models.models import CryptoEntry
from app.models.errors import InvalidTime, UnavailableTime
from datetime import datetime
import logging
import asyncio

CURRENT_SEARCH_SECONDS_RANGE = 60
HISTORICAL_SEARCH_SECONDS_RANGE = 60 * 60 * 24


class CoinResolver:
    db: Database
    coin_market_cap: CoinMarketCap
    crypto_compare: CryptoCompare
    time_service: TimeService
    db_tasks: set[asyncio.Task]

    def __init__(self, db: Database, coin_market_cap: CoinMarketCap, crypto_compare: CryptoCompare, time_service: TimeService):
        self.db = db
        self.coin_market_cap = coin_market_cap
        self.crypto_compare = crypto_compare
        self.time_service = time_service
        self.db_tasks = set()
        logging.debug("CoinResolver: Initialized coin resolver")

    def close(self):
        self.db.close()
        logging.debug("CoinResolver: Closed coin resolver")

    async def fetch_top_coins(self, limit: int, timestamp: datetime | None) -> list[CryptoEntry]:
        if (timestamp_for_query := self._get_fetch_timestamp(timestamp)) is not None:
            logging.info(
                f"CoinResolver: Fetching coins from DB with timestamp {timestamp_for_query.strftime(time_format)}")
            return self._fetch_top_coins_from_database(limit, timestamp_for_query)
        else:
            logging.info(f"CoinResolver: Fetching coins from remote source")

            # Fetch coins from remote source
            top_coins = await self._fetch_top_coins_from_API_services()

            # Store in DB for historical data in the background
            db_task = asyncio.create_task(
                self.db.insert_updated_data(top_coins))
            self.db_tasks.add(db_task)
            db_task.add_done_callback(self.db_tasks.discard)

            # Return within limit
            return top_coins[0:limit]

    def _get_fetch_timestamp(self, reference: datetime | None) -> datetime | None:
        now = self.time_service.now()
        # No reference was given, we are performing a current search
        if reference is None:
            # If we fetched recently, return that timestamp
            if (closest_timestamp := self.db.get_closest_timestamp(now, CURRENT_SEARCH_SECONDS_RANGE)) is not None:
                return closest_timestamp
            # Otherwise, return None
            else:
                return None

        # We are querying for historical data.
        # If we have a close-enough timestamp in the db, use that
        if (closest_timestamp := self.db.get_closest_timestamp(reference, HISTORICAL_SEARCH_SECONDS_RANGE)) is not None:
            return closest_timestamp

        # If it's not found, we don't have it
        raise UnavailableTime()

    def _fetch_top_coins_from_database(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return self.db.get_historical_data(limit, timestamp)

    async def _fetch_top_coins_from_API_services(self) -> list[CryptoEntry]:
        now = self.time_service.now()

        # Fetch network data in parallel
        coin_prices, top_crypto = await asyncio.gather(
            self.coin_market_cap.get_coin_prices(),
            self.crypto_compare.get_top_crypto_list()
        )

        # Merge results
        top_crypto_with_price: list[CryptoEntry] = []
        for idx, coin in enumerate(top_crypto):
            if (value := coin_prices.get(coin)) is not None:
                cryptoEntry = CryptoEntry(
                    name=coin,
                    value=value,
                    rank=idx+1,
                    timestamp=now
                )
                top_crypto_with_price.append(cryptoEntry)

        return top_crypto_with_price
