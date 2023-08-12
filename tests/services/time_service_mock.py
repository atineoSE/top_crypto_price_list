from datetime import datetime


class TimeServiceMock:
    time: datetime

    def __init__(self, time: datetime):
        self.time = time

    def now(self) -> datetime:
        return self.time
