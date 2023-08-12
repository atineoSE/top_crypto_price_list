class CoinMarketCapMock:
    async def get_coin_prices(self) -> dict[str, float]:
        return {}
