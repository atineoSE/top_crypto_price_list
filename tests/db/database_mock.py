from datetime import datetime
from app.models.models import CryptoEntry


class DatabaseMock:
    async def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        return None

    def get_closest_timestamp(self, timestamp: datetime, seconds_range: int) -> datetime | None:
        return None

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return []
