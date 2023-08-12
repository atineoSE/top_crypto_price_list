from datetime import datetime
from app.models.errors import InvalidTime

time_format = '%Y-%m-%d %H:%M:%S'


class TimeService:
    def now(self) -> datetime:
        return datetime.now()

    def parse_time(self, time_description: str) -> datetime:
        try:
            timestamp = datetime.strptime(time_description, time_format)
        except ValueError:
            raise InvalidTime()

        return timestamp
