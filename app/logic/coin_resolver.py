from app.db.database import Database
from app.services.coin_market_cap import CoinMarketCap
from app.services.crypto_compare import CryptoCompare
from app.services.time_service import TimeService
from app.models.models import CryptoEntry
from app.models.errors import UnavailableTime
from datetime import datetime
import logging
import asyncio

CURRENT_SEARCH_SECONDS_RANGE = 60
HISTORICAL_SEARCH_SECONDS_RANGE = 60 * 60 * 24


class CoinResolver:
    """Resolves coin data from different sources: 
    external API services for current time queries and database for historical queries.
    """
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
        """Frees up resources."""
        self.db.close()
        logging.debug("CoinResolver: Closed coin resolver")

    async def fetch_top_coins(self, limit: int, timestamp: datetime | None) -> list[CryptoEntry]:
        """Fetches top coins by market volume.

        This function operates in one of two modes: "current" or "historical".
        If there is no timestamp given, the "current" mode is used.
        If there is a timestamp given, the "historical" mode is used.

        When in "current" more, updated coin data is retrieved from external API services,
        unless another current query has been performed within CURRENT_SEARCH_SECONDS_RANGE,
        in which case the cached result is returned.

        Coin data retrieved from external services is stored in the database so that it
        becomes available for historical queries.

        When in "historical" mode, the coin data is retrieved from the database, if available.
        If not available, an UnavailableTime exception is raised.

        Args:
            limit (int): The number of coins to return.
            timestamp (datetime, optional): The timestamp to use for historical queries. Defaults to None.

        Raises:
            UnavailableTime: If we hold no data in the database for the requested timestamp.

        Returns:
            list[CryptoEntry]: a list of CryptoEntry objects.
        """
        if (timestamp_for_query := self._get_fetch_timestamp(timestamp)) is not None:
            logging.info(
                f"CoinResolver: Fetching coins from DB with timestamp {timestamp_for_query.isoformat()}")
            return self.db.get_historical_data(limit, timestamp_for_query)
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
        # No reference was given, we are performing a current search
        if reference is None:
            # If we fetched recently, return that timestamp
            now = self.time_service.now()
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
        logging.debug(
            f"CoinResolver: could not find any timestamp for historical data around {reference.isoformat()}")
        raise UnavailableTime()

    async def _fetch_top_coins_from_API_services(self) -> list[CryptoEntry]:
        now = self.time_service.now()

        # Fetch network data in parallel
        coin_prices, top_crypto = await asyncio.gather(
            self.coin_market_cap.get_coin_prices(),
            self.crypto_compare.get_top_crypto_list()
        )

        # Merge results
        top_crypto_with_price: list[CryptoEntry] = []
        idx = 1
        for coin_symbol, coin_name in top_crypto:
            # Try match by symbol
            value = coin_prices.get(coin_symbol)
            if value is None:
                # If we couldn't find it, try match by name
                value = coin_prices.get(coin_name)

            if value is not None:
                cryptoEntry = CryptoEntry(
                    name=coin_symbol,
                    value=value,
                    rank=idx,
                    timestamp=now
                )
                top_crypto_with_price.append(cryptoEntry)
                idx += 1
            else:
                logging.debug(
                    f"CoinResolver: could not find price for {coin_symbol}. Skipping.")

        return top_crypto_with_price
