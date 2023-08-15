from datetime import datetime, timezone


class TimeService:
    """A wrapper class for time services"""

    def now(self) -> datetime:
        """"Current time in UTC timezone"""
        return datetime.now(timezone.utc)

    def parse_time(self, time_description: str) -> datetime:
        """Parses input description into a datetime object in UTC timezone."""
        return datetime.fromisoformat(time_description).replace(tzinfo=timezone.utc)
