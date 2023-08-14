from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from app.models.models import CryptoEntry
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

    async def insert_updated_data(self, crypto_entries: list[CryptoEntry]) -> None:
        crypto_entries_for_insertion = map(
            lambda x: x.model_dump(mode="json"), crypto_entries)
        self.collection.insert_many(crypto_entries_for_insertion)

    def get_closest_timestamp(self, timestamp: datetime, seconds_range: int) -> datetime | None:
        try:
            close_timestamps = self.collection.aggregate([
                # {"$match":
                #     {"and":
                #         [
                #             {"timestamp": {"$lte": timestamp +
                #                            timedelta(seconds=seconds_range/2)}},
                #             {"timestamp": {"$gte": timestamp -
                #                            timedelta(seconds=seconds_range/2)}}
                #         ]
                #      }
                #  },
                {"$group":
                    {
                        "_id": None,
                        "timestamp": {"$addToSet": "$timestamp"}
                    }
                 }
            ])
            alive = close_timestamps.alive
            value = list(map(lambda t: datetime.fromisoformat(t),
                         close_timestamps.next()["timestamp"]))
            return self._closest_timestamp(timestamp, value)
        except StopIteration:
            return None

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        results = self.collection.find(
            {"timestamp": timestamp}).sort("rank", -1).limit(limit)
        converted_results = []
        for result in results:
            print(result)
            cryptoEntry = CryptoEntry(**result)
            converted_results.append(cryptoEntry)
        # converted_results = list(map(lambda x: CryptoEntry(**x), results))
        return converted_results

    def _closest_timestamp(self, reference: datetime, timestamps: list[datetime]) -> datetime | None:
        if len(timestamps) == 0:
            return None
        closest = timestamps[0]
        min_diff = reference - closest
        for elem in timestamps:
            diff = reference - elem
            if diff < min_diff:
                closest = elem
                min_diff = diff
        return closest
