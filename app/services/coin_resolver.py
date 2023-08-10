from db.database import Database
from services.coin_market_cap import CoinMarketCap
from services.crypto_compare import CryptoCompare
from datetime import datetime
from models.models import CryptoEntry

REFRESH_PERIOD_IN_SECONDS = 60


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

    def fetch_top_coins(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        if self._should_fetch_locally(timestamp):
            return self._fetch_top_coins_locally(limit, timestamp)
        else:
            # Fetch coins from remote source
            top_coins = self._fetch_top_coins_remotely(timestamp)
            # Store in DB for historical data
            self.db.insert_updated_data(top_coins)
            # Track update
            last_update = timestamp
            # Return within limit
            return top_coins[0:limit]

    def _should_fetch_locally(self, timestamp: datetime) -> bool:
        return True

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
