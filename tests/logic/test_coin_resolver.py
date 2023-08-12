import pytest
import asyncio
from app.logic.coin_resolver import CoinResolver, CURRENT_SEARCH_SECONDS_RANGE, HISTORICAL_SEARCH_SECONDS_RANGE
from app.models.models import CryptoEntry
from app.services.time_service import time_format
from tests.db.database_mock import DatabaseMock
from tests.services.coin_market_cap_mock import CoinMarketCapMock
from tests.services.crypto_compare_mock import CryptoCompareMock
from tests.services.time_service_mock import TimeServiceMock
from datetime import datetime, timedelta

SAMPLE_TIME = datetime.strptime("2023-08-12 17:00:00", time_format)
SAMPLE_TIME_SHORTLY_AFTER = SAMPLE_TIME + \
    timedelta(seconds=CURRENT_SEARCH_SECONDS_RANGE-1)
SAMPLE_TIME_LONG_AFTER = SAMPLE_TIME + \
    timedelta(seconds=CURRENT_SEARCH_SECONDS_RANGE)
SAMPLE_PREVIOUS_TIME_WITHIN_HISTORICAL_RANGE = SAMPLE_TIME - \
    timedelta(seconds=HISTORICAL_SEARCH_SECONDS_RANGE-1)
SAMPLE_PREVIOUS_TIME_BEYOND_HISTORICAL_RANGE = SAMPLE_TIME - \
    timedelta(seconds=HISTORICAL_SEARCH_SECONDS_RANGE)

SAMPLE_COIN_PRICES = {"BTC": 29434.824505477198, "ETH": 1851.0382543598475}
SAMPLE_COIN_PRICES_AFTER = {"ETH": 2500, "BTC": 1800}
SAMPLE_TOP_CRYPTO = ["BTC", "ETH"]
SAMPLE_TOP_CRYPTO_AFTER = ["ETH", "BTC"]
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


@pytest.mark.asyncio
async def test_current_fetch_for_top_coins_retrieves_data_from_API_services():
    # Arrange
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act
    results = await sut.fetch_top_coins(2, None)

    # Assert
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 1
    assert crypto_compare_mock.num_invocations == 1


@pytest.mark.asyncio
async def test_current_fetch_for_top_coins_shortly_after_a_previous_fetch_returns_cached_data():
    # Arrange
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act and assert
    results = await sut.fetch_top_coins(2, None)
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 1
    assert crypto_compare_mock.num_invocations == 1

    # Wait until db insertion is done
    while len(db_mock.historical_data) == 0:
        await asyncio.sleep(0.1)

    # Act and assert
    time_service_mock.time = SAMPLE_TIME_SHORTLY_AFTER
    results = await sut.fetch_top_coins(2, None)
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 1
    assert coin_market_cap_mock.num_invocations == 1
    assert crypto_compare_mock.num_invocations == 1


@pytest.mark.asyncio
async def test_current_fetch_for_top_coins_long_after_a_previous_fetch_retrieves_data_from_API_services_again():
    # Arrange
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act and assert
    results = await sut.fetch_top_coins(2, None)
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 1
    assert crypto_compare_mock.num_invocations == 1

    # Act and assert
    time_service_mock.time = SAMPLE_TIME_LONG_AFTER
    coin_market_cap_mock.coin_prices = SAMPLE_COIN_PRICES_AFTER
    crypto_compare_mock.top_crypto_list = SAMPLE_TOP_CRYPTO_AFTER
    results = await sut.fetch_top_coins(2, None)
    assert SAMPLE_RESULTS_LONG_AFTER == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 2
    assert crypto_compare_mock.num_invocations == 2


@pytest.mark.asyncio
async def test_historical_fetch_for_top_coins_retrieves_data_from_database_if_found():
    pass


@pytest.mark.asyncio
async def test_historical_fetch_for_top_coins_throws_error_if_database_is_missing_data():
    pass
