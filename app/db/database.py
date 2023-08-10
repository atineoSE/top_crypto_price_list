from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from models.models import CryptoEntry
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection

load_dotenv()

db_password = os.getenv("DB_PASSWORD")


class Database:
    client: MongoClient
    collection: Collection

    def __init__(self):
        CONNECTION_STRING = "mongodb+srv://admin:" + \
            db_password + "@cluster0.0maxtet.mongodb.net"
        self.client = MongoClient(CONNECTION_STRING)
        self.collection = self.client["crypto"]["top_assets"]

    def close(self):
        self.client.close()

    def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        self.collection.insert_many(crypto_entries)

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        results = self.collection.find(
            {"and":
                [
                    {"timestamp": {"$lt": timestamp}},
                    {"timestamp": {"$gt": timestamp - timedelta(days=1)}}
                ]
             },
        ).sort("timestamp").sort("rank", -1).limit(limit)

        return list(map(lambda x: CryptoEntry(**x), results))

    def get_last_update(self) -> datetime | None:
        if (result := self.collection.find().sort("timestamp")).limit(1) is not None:
            return result[0]["timestamp"]
        else:
            return None
