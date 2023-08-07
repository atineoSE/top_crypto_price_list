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
        self.last_update = None

    def close(self):
        self.db.close()

    def fetch_top_coins(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return []
