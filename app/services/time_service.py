from datetime import datetime, timezone


class TimeService:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def parse_time(self, time_description: str) -> datetime:
        return datetime.fromisoformat(time_description).replace(tzinfo=timezone.utc)
