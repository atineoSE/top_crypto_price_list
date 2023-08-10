from db.database import Database
from services.coin_market_cap import CoinMarketCap
from services.crypto_compare import CryptoCompare
from datetime import datetime, timedelta
from models.models import CryptoEntry
from models.errors import InvalidTime, UnavailableTime

CURRENT_SEARCH_SECONDS_RANGE = 60
HISTORICAL_SEARCH_SECONDS_RANGE = 60 * 60 * 24


class CoinResolver:
    db: Database
    coin_market_cap: CoinMarketCap
    crypto_compare: CryptoCompare
    last_update: datetime | None

    def __init__(self):
        self.db = Database()
        self.coin_market_cap = CoinMarketCap()
        self.crypto_compare = CryptoCompare()
        self.last_update = self.db.get_last_update()

    def close(self):
        self.db.close()

    def fetch_top_coins(self, limit: int, timestamp: datetime | None) -> list[CryptoEntry]:
        if (timestamp_for_query := self._get_fetch_timestamp(timestamp)) is not None:
            return self._fetch_top_coins_locally(limit, timestamp_for_query)
        else:
            # Fetch coins from remote source
            top_coins = self._fetch_top_coins_remotely(timestamp)
            # Store in DB for historical data
            self.db.insert_updated_data(top_coins)
            # Track update
            last_update = datetime.now()
            # Return within limit
            return top_coins[0:limit]

    def _get_fetch_timestamp(self, reference: datetime | None) -> datetime | None:
        # If no reference is provided, fetch now
        if reference is None:
            return None

        # If querying about the future, raise error
        time_difference = datetime.now() - reference
        if time_difference.total_seconds < 0:
            raise InvalidTime()

        # If we have a close-enough timestamp in the db, use that
        seconds_range = CURRENT_SEARCH_SECONDS_RANGE if reference is None else HISTORICAL_SEARCH_SECONDS_RANGE
        if (closest_timestamp := self.db.get_closest_timestamp(reference, seconds_range)) is not None:
            return closest_timestamp

        # If it's not found, we don't have it
        raise UnavailableTime()

    def _fetch_top_coins_locally(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return self.db.get_historical_data(limit, timestamp)

    def _fetch_top_coins_remotely(self, timestamp: datetime) -> list[CryptoEntry]:
        # Fetch network data
        coin_prices = self.coin_market_cap.get_coin_prices()
        top_crypto = self.crypto_compare.get_top_crypto_list()

        # Merge results
        top_crypto_with_price: list[CryptoEntry] = []
        for idx, coin in enumerate(top_crypto):
            if (value := coin_prices.get(coin)) is not None:
                cryptoEntry = CryptoEntry(
                    name=coin,
                    value=value,
                    rank=idx,
                    timestamp=timestamp
                )
                top_crypto_with_price.append(cryptoEntry)

        return top_crypto_with_price
