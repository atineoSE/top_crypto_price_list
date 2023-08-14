from datetime import datetime, timedelta, timezone
from app.services.time_service import TimeService
from app.logic.coin_resolver import CURRENT_SEARCH_SECONDS_RANGE, HISTORICAL_SEARCH_SECONDS_RANGE


SAMPLE_TIME = datetime.fromisoformat(
    "2023-08-12T17:00:00").replace(tzinfo=timezone.utc)
SAMPLE_TIME_SHORTLY_AFTER = SAMPLE_TIME + \
    timedelta(seconds=CURRENT_SEARCH_SECONDS_RANGE-1)
SAMPLE_TIME_LONG_AFTER = SAMPLE_TIME + \
    timedelta(seconds=CURRENT_SEARCH_SECONDS_RANGE)
SAMPLE_PREVIOUS_TIME_WITHIN_HISTORICAL_RANGE = SAMPLE_TIME - \
    timedelta(seconds=HISTORICAL_SEARCH_SECONDS_RANGE)
SAMPLE_PREVIOUS_TIME_BEYOND_HISTORICAL_RANGE = SAMPLE_TIME - \
    timedelta(seconds=HISTORICAL_SEARCH_SECONDS_RANGE+1)


class TimeServiceMock(TimeService):
    time: datetime

    def __init__(self, time: datetime):
        self.time = time

    def now(self) -> datetime:
        return self.time
