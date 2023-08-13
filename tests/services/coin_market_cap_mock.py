SAMPLE_COIN_PRICES = {"BTC": 29434.824505477198, "ETH": 1851.0382543598475}
SAMPLE_COIN_PRICES_LATER = {"ETH": 2500, "BTC": 1800}


class CoinMarketCapMock:
    coin_prices: dict[str, float]
    num_invocations: int

    def __init__(self, coin_prices: dict[str, float] = {}):
        self.coin_prices = coin_prices
        self.num_invocations = 0

    async def get_coin_prices(self) -> dict[str, float]:
        self.num_invocations += 1
        return self.coin_prices
