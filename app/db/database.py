from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from models import CryptoEntry

load_dotenv()

db_password = os.getenv("DB_PASSWORD")


class Database:
    def __init__(self):
        CONNECTION_STRING = "mongodb+srv://admin:" + \
            db_password + "@cluster0.0maxtet.mongodb.net"
        self.client = MongoClient(CONNECTION_STRING)["crypto"]

    def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        self.client.insert_many(crypto_entries)

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        return self.client.find(
            {"and":
                [
                    {"timestamp": {"$lt": timestamp}},
                    {"timestamp": {"$gt": timestamp - timedelta(days=1)}}
                ]
             },
        ).sort("timestamp").sort("rank", -1).limit(limit)
