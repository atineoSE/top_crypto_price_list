class CoinMarketCapMock:
    coin_prices: dict[str, float]
    num_invocations: int

    def __init__(self, coin_prices: dict[str, float] = {}):
        self.coin_prices = coin_prices
        self.num_invocations = 0

    async def get_coin_prices(self) -> dict[str, float]:
        self.num_invocations += 1
        return self.coin_prices
