from datetime import datetime

from app.models.models import CryptoEntry
from app.models.errors import UnavailableTime

from tests.services.time_service_mock import SAMPLE_TIME, SAMPLE_TIME_LONG_AFTER

SAMPLE_RESULTS = [
    CryptoEntry(name="BTC", value=29434.824505477198,
                rank=1, timestamp=SAMPLE_TIME),
    CryptoEntry(name="ETH", value=1851.0382543598475,
                rank=2, timestamp=SAMPLE_TIME)
]
SAMPLE_RESULTS_LONG_AFTER = [
    CryptoEntry(name="ETH", value=2500,
                rank=1, timestamp=SAMPLE_TIME_LONG_AFTER),
    CryptoEntry(name="BTC", value=1800,
                rank=2, timestamp=SAMPLE_TIME_LONG_AFTER)
]
SAMPLE_RESULTS_JSON = '[\
    {\
        "name": "BTC",\
        "value": 29434.824505477198,\
        "rank": 1,\
        "timestamp": "2023-08-12T17:00:00+00:00"\
    },\
    {\
        "name": "ETH",\
        "value": 1851.0382543598475,\
        "rank": 2,\
        "timestamp": "2023-08-12T17:00:00+00:00"\
    }\
]\
'
SAMPLE_RESULTS_CSV = """\
rank,symbol,price_USD,timestamp
1,BTC,29434.824505477198,2023-08-12T17:00:00+00:00
2,ETH,1851.0382543598475,2023-08-12T17:00:00+00:00
"""


class CoinResolverMock:
    results: list[CryptoEntry] | None

    def __init__(self, results: list[CryptoEntry] | None = None):
        self.results = results

    async def fetch_top_coins(self, limit: int, timestamp: datetime | None) -> list[CryptoEntry]:
        if self.results is None:
            raise UnavailableTime
        return self.results
