from datetime import datetime

time_format = '%Y-%m-%d %H:%M:%S'


class TimeService:
    def now(self) -> datetime:
        return datetime.now()
