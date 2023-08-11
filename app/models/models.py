from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import json

time_format = '%Y-%m-%d %H:%M:%S'


class CryptoEntry(BaseModel):
    name: str
    value: float
    rank: int
    timestamp: datetime


class OutputFormat(Enum):
    JSON = "JSON"
    CSV = "CSV"

    def output(self, crypto_entries: list[CryptoEntry]) -> list[CryptoEntry] | str:
        if self == OutputFormat.JSON:
            return crypto_entries
        else:
            output = ""
            for crypto_entry in crypto_entries:
                output += f"{crypto_entry.name},{crypto_entry.value},{crypto_entry.rank},{crypto_entry.timestamp}\n"
            return output
