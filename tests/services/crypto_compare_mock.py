class CryptoCompareMock:
    top_crypto_list: list[str]

    def __init__(self, top_crypto_list: list[str] = []):
        self.top_crypto_list = top_crypto_list

    async def get_top_crypto_list(self) -> list[str]:
        return self.top_crypto_list
