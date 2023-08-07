from db.database import Database
from services.coin_market_cap import CoinMarketCap
from services.crypto_compare import CryptoCompare
from datetime import datetime
from models.models import CryptoEntry


class CoinResolver:
    def __init__(self):
        self.db = Database()
        self.coin_market_cap = CoinMarketCap()
        self.crypto_compare = CryptoCompare()

    def close(self):
        self.db.close()

    def fetch_top_coins(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return []
