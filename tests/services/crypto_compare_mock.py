class CryptoCompareMock:
    top_crypto_list: list[str]
    num_invocations: int

    def __init__(self, top_crypto_list: list[str] = []):
        self.top_crypto_list = top_crypto_list
        self.num_invocations = 0

    async def get_top_crypto_list(self) -> list[str]:
        self.num_invocations += 1
        return self.top_crypto_list
