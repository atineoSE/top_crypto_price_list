from datetime import datetime
from app.models.models import CryptoEntry


class DatabaseMock:
    closest_timestamp: datetime | None
    historical_data: list[CryptoEntry]

    def __init__(self, closest_timestamp: datetime | None = None, historical_data: list[CryptoEntry] = []):
        self.closest_timestamp = closest_timestamp
        self.historical_data = historical_data

    async def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        pass

    def get_closest_timestamp(self, timestamp: datetime, seconds_range: int) -> datetime | None:
        return self.closest_timestamp

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return self.historical_data
