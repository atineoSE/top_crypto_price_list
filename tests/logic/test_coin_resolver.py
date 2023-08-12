import pytest
from app.logic.coin_resolver import CoinResolver
from tests.db.database_mock import DatabaseMock
from tests.services.coin_market_cap_mock import CoinMarketCapMock
from tests.services.crypto_compare_mock import CryptoCompareMock


@pytest.mark.asyncio
async def test_fetching_top_coins_now_returns_coins():
    db_mock = DatabaseMock()
    coin_market_cap_mock = CoinMarketCapMock()
    crypto_compare_mock = CryptoCompareMock()
    sut = CoinResolver(db_mock, coin_market_cap_mock, crypto_compare_mock)
