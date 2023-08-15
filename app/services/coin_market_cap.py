from dotenv import load_dotenv
import os
import requests
from typing import Any, cast
import logging
import time
import asyncio

load_dotenv()

COIN_MARKET_CAP_API_KEY = os.getenv("COIN_MARKET_CAP_API_KEY")


class CoinMarketCap:
    host: str
    headers: dict[str, Any]

    def __init__(self):
        self.host = "https://pro-api.coinmarketcap.com/v1/"
        self.headers = {
            "Accept": "application/json",
            "X-CMC_PRO_API_KEY": COIN_MARKET_CAP_API_KEY
        }

    async def get_coin_prices(self) -> dict[str, float]:
        url = self.host + "cryptocurrency/listings/latest"
        url_params: dict[str, Any] = {
            "limit": 500,
            "sort": "volume_24h",
            "convert": "USD"
        }
        logging.debug(
            f"CoinMarketCap: starting request at {time.strftime('%X')}")
        response = requests.get(url, headers=self.headers, params=url_params)
        data = response.json()["data"]
        coin_prices: dict[str, float] = {}
        for item in data:
            # Add relation by symbol
            name = item["symbol"]
            value = item["quote"]["USD"]["price"]
            coin_prices[name] = value

            # Add relation by name
            name = item["name"]
            coin_prices[name] = value

        logging.debug(
            f"CoinMarketCap: Got following coin prices: \n{coin_prices}")

        return coin_prices
