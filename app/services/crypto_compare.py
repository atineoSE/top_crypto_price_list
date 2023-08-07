from dotenv import load_dotenv
import os
import requests
from typing import Any, cast

load_dotenv()

CRYPTO_COMPARE_API_KEY = os.getenv("CRYPTO_COMPARE_API_KEY")


class CryptoCompare:
    host: str
    headers: dict[str, Any]

    def __init__(self):
        self.host = "https://min-api.cryptocompare.com/"
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Apikey {}".format(CRYPTO_COMPARE_API_KEY)
        }

    def get_top_crypto_list(self) -> list[str]:
        url = self.host + "data/top/totalvolfull"
        url_params: dict[str, Any] = {
            "limit": 100
        }
        response = requests.get(url, headers=self.headers, params=url_params)
        data = response.json()["Data"]
        top_crypto_list = map(
            lambda x: (x["CoinInfo"]["Name"]),
            data
        )
        return cast(list[str], top_crypto_list)
