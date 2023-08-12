class CoinMarketCapMock:
    coin_prices: dict[str, float]

    def __init__(self, coin_prices: dict[str, float] = {}):
        self.coin_prices = coin_prices

    async def get_coin_prices(self) -> dict[str, float]:
        return self.coin_prices
