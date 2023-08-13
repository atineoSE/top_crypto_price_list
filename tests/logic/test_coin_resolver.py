import pytest
import asyncio
from datetime import datetime, timedelta

from app.logic.coin_resolver import CoinResolver, CURRENT_SEARCH_SECONDS_RANGE, HISTORICAL_SEARCH_SECONDS_RANGE
from app.models.models import CryptoEntry
from app.models.errors import UnavailableTime
from app.services.time_service import time_format

from tests.db.database_mock import DatabaseMock
from tests.services.coin_market_cap_mock import CoinMarketCapMock, SAMPLE_COIN_PRICES, SAMPLE_COIN_PRICES_LATER
from tests.services.crypto_compare_mock import CryptoCompareMock, SAMPLE_TOP_CRYPTO, SAMPLE_TOP_CRYPTO_LATER
from tests.services.time_service_mock import TimeServiceMock
from tests.services.time_service_mock import SAMPLE_TIME, SAMPLE_TIME_SHORTLY_AFTER, SAMPLE_TIME_LONG_AFTER
from tests.services.time_service_mock import SAMPLE_PREVIOUS_TIME_WITHIN_HISTORICAL_RANGE, SAMPLE_PREVIOUS_TIME_BEYOND_HISTORICAL_RANGE
from tests.logic.coin_resolver_mock import SAMPLE_RESULTS, SAMPLE_RESULTS_LONG_AFTER


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
    coin_market_cap_mock.coin_prices = SAMPLE_COIN_PRICES_LATER
    crypto_compare_mock.top_crypto_list = SAMPLE_TOP_CRYPTO_LATER
    results = await sut.fetch_top_coins(2, None)
    assert SAMPLE_RESULTS_LONG_AFTER == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 2
    assert crypto_compare_mock.num_invocations == 2


@pytest.mark.asyncio
async def test_historical_fetch_for_top_coins_retrieves_data_from_database_if_exact_timestamp_is_found():
    # Arrange
    db_mock = DatabaseMock(SAMPLE_TIME, SAMPLE_RESULTS)
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act
    results = await sut.fetch_top_coins(2, SAMPLE_TIME)

    # Assert
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 1
    assert coin_market_cap_mock.num_invocations == 0
    assert crypto_compare_mock.num_invocations == 0


@pytest.mark.asyncio
async def test_historical_fetch_for_top_coins_retrieves_data_from_database_if_timestamp_within_range_is_found():
    # Arrange
    db_mock = DatabaseMock(SAMPLE_TIME, SAMPLE_RESULTS)
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act
    results = await sut.fetch_top_coins(2, SAMPLE_PREVIOUS_TIME_WITHIN_HISTORICAL_RANGE)

    # Assert
    assert SAMPLE_RESULTS == results
    assert db_mock.num_historical_data_fetches == 1
    assert coin_market_cap_mock.num_invocations == 0
    assert crypto_compare_mock.num_invocations == 0


@pytest.mark.asyncio
async def test_historical_fetch_for_top_coins_raises_error_if_timestamp_within_range_is_not_found():
    # Arrange
    db_mock = DatabaseMock(SAMPLE_TIME, SAMPLE_RESULTS)
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act and assert
    with pytest.raises(UnavailableTime):
        results = await sut.fetch_top_coins(2, SAMPLE_PREVIOUS_TIME_BEYOND_HISTORICAL_RANGE)


@pytest.mark.asyncio
async def test_fetch_for_top_coins_returns_number_of_results_given_in_limit():
    # Arrange
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock(SAMPLE_COIN_PRICES)
    crypto_compare_mock = CryptoCompareMock(SAMPLE_TOP_CRYPTO)
    time_service_mock = TimeServiceMock(SAMPLE_TIME)

    sut = CoinResolver(db_mock, coin_market_cap_mock,
                       crypto_compare_mock, time_service_mock)

    # Act
    results = await sut.fetch_top_coins(1, None)

    # Assert
    assert SAMPLE_RESULTS[:1] == results
    assert db_mock.num_historical_data_fetches == 0
    assert coin_market_cap_mock.num_invocations == 1
    assert crypto_compare_mock.num_invocations == 1
