from datetime import datetime


class TimeService:
    def now(self) -> datetime:
        return datetime.now()
