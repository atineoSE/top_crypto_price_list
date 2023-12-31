from dotenv import load_dotenv
import os
import requests
from typing import Any, cast
import logging
import time
import asyncio

load_dotenv()

CRYPTO_COMPARE_API_KEY = os.getenv("CRYPTO_COMPARE_API_KEY")


class CryptoCompare:
    """API external service for CryptoCompare"""
    host: str
    headers: dict[str, Any]

    def __init__(self):
        self.host = "https://min-api.cryptocompare.com/"
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Apikey {}".format(CRYPTO_COMPARE_API_KEY)
        }

    async def get_top_crypto_list(self) -> list[tuple[str, str]]:
        """Gets symbol name and full name of the top 100 crypto currencies sorted by market volume in the last 24 hours.

        Returns:
            list[tuple[str, str]]: List of tuples of crypto currency symbol name and full name.
            For example: [("BTC", "Bitcoin"), ("ETH", "Ethereum"), ...]
        """
        url = self.host + "data/top/totalvolfull"
        url_params: dict[str, Any] = {
            "limit": 100,
            "tsym": "USD"
        }
        logging.debug(
            f"CryptoCompare: starting request at {time.strftime('%X')}")
        response = requests.get(url, headers=self.headers, params=url_params)
        data = response.json()["Data"]
        top_crypto = list(map(
            lambda x: (x["CoinInfo"]["Name"], x["CoinInfo"]["FullName"]),
            data
        ))

        logging.debug(
            f"CryptoCompare: Got following top coins: \n{top_crypto}")

        return top_crypto
