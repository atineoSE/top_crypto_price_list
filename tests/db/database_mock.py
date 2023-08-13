from datetime import datetime, timedelta
from app.models.models import CryptoEntry


class DatabaseMock:
    closest_timestamp: datetime | None
    historical_data: list[CryptoEntry]
    num_historical_data_fetches: int

    def __init__(self, closest_timestamp: datetime | None = None, historical_data: list[CryptoEntry] = []):
        self.closest_timestamp = closest_timestamp
        self.historical_data = historical_data
        self.num_historical_data_fetches = 0

    async def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        self.historical_data = crypto_entries
        if len(crypto_entries) > 0:
            self.closest_timestamp = crypto_entries[0].timestamp

    def get_closest_timestamp(self, timestamp: datetime, seconds_range: int) -> datetime | None:
        if (closest_timestamp := self.closest_timestamp) is not None:
            if (closest_timestamp - timedelta(seconds=seconds_range)) <= timestamp <= (closest_timestamp + timedelta(seconds=seconds_range)):
                return self.closest_timestamp

        return None

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        self.num_historical_data_fetches += 1
        return self.historical_data
