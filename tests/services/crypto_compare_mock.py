SAMPLE_TOP_CRYPTO = [("BTC", "Bitcoin"), ("ETH", "Ethereum")]
SAMPLE_TOP_CRYPTO_LATER = [("ETH", "Ethereum"), ("BTC", "Bitcoin")]


class CryptoCompareMock:
    top_crypto_list: list[tuple[str, str]]
    num_invocations: int

    def __init__(self, top_crypto_list: list[tuple[str, str]] = []):
        self.top_crypto_list = top_crypto_list
        self.num_invocations = 0

    async def get_top_crypto_list(self) -> list[tuple[str, str]]:
        self.num_invocations += 1
        return self.top_crypto_list
