from datetime import datetime


class TimeServiceMock:
    time: datetime

    def __init__(self, time: datetime):
        self.time = time

    def now(self) -> datetime:
        return self.time

    def parse_time(self, time_description: str) -> datetime:
        return self.time
