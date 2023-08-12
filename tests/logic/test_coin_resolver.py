import pytest
from app.logic.coin_resolver import CoinResolver
from app.models.models import CryptoEntry
from app.services.time_service import time_format
from tests.db.database_mock import DatabaseMock
from tests.services.coin_market_cap_mock import CoinMarketCapMock
from tests.services.crypto_compare_mock import CryptoCompareMock
from tests.services.time_service_mock import TimeServiceMock
from datetime import datetime

sample_time = datetime.strptime("2023-08-12 17:00:00", time_format)
sample_coin_prices = {"BTC": 29434.824505477198, "ETH": 1851.0382543598475}
sample_top_crypto = ["BTC", "ETH"]
sample_results = [
    CryptoEntry(name="BTC", value=29434.824505477198,
                rank=1, timestamp=sample_time),
    CryptoEntry(name="ETH", value=1851.0382543598475,
                rank=2, timestamp=sample_time)
]


@pytest.mark.asyncio
async def test_fetching_top_coins_now_returns_coins():
    # Arrange
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock(sample_coin_prices)
    crypto_compare_mock = CryptoCompareMock(sample_top_crypto)
    time_service_mock = TimeServiceMock(sample_time)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act
    results = await sut.fetch_top_coins(2, None)

    # Assert
    assert sample_results == results
