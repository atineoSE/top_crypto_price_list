from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from app.models.models import CryptoEntry
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
import logging

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
        max_timestamp = timestamp + timedelta(seconds=seconds_range/2)
        min_timestamp = timestamp - timedelta(seconds=seconds_range/2)
        try:
            close_timestamps_cursor = self.collection.aggregate([
                {"$match":
                    {"$and":
                        [
                            {"timestamp": {"$lte": max_timestamp.isoformat()}},
                            {"timestamp": {"$gte": min_timestamp.isoformat()}}
                        ]
                     }
                 },
                {"$group":
                    {
                        "_id": None,
                        "timestamp": {"$addToSet": "$timestamp"}
                    }
                 }
            ])
            close_timestamps = list(map(lambda t: datetime.fromisoformat(t),
                                        close_timestamps_cursor.next()["timestamp"]))
            logging.debug(
                f"Database: found {len(close_timestamps)} between {min_timestamp.isoformat()} and {max_timestamp.isoformat()}")
            return self._closest_timestamp(timestamp, close_timestamps)
        except StopIteration:
            logging.debug(
                f"Database: Couldn't find any timestamps between {min_timestamp.isoformat()} and {max_timestamp.isoformat()}")
            return None

    def get_historical_data(self, limit: int, timestamp: datetime) -> list[CryptoEntry]:
        results = self.collection.find(
            {"timestamp": timestamp.isoformat()}).sort("rank").limit(limit)
        converted_results = list(map(lambda x: CryptoEntry(**x), results))
        logging.debug(
            f"Database: retrieved {len(converted_results)} records of historical data with timestamp {timestamp.isoformat()}")
        return converted_results

    def _closest_timestamp(self, reference: datetime, timestamps: list[datetime]) -> datetime | None:
        logging.debug(
            f"Database: looking for the closest time to {reference.isoformat()} in {list(map(lambda t: t.isoformat(), timestamps))}")
        if len(timestamps) == 0:
            return None
        closest = timestamps[0]
        min_diff = reference - closest
        for elem in timestamps:
            diff = reference - elem
            if diff < min_diff:
                closest = elem
                min_diff = diff
        logging.debug(f"Database: found closest time: {closest.isoformat()}")
        return closest
