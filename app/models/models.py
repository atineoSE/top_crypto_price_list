from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import json
from typing import Any


class CryptoEntry(BaseModel):
    name: str
    value: float
    rank: int
    timestamp: datetime


class OutputFormat(Enum):
    JSON = "JSON"
    CSV = "CSV"

    def output(self, crypto_entries: list[CryptoEntry]) -> Any:
        if self == OutputFormat.JSON:
            return list(map(lambda x: x.model_dump(mode="json"), crypto_entries))
        else:
            output = "rank,symbol,price_USD,timestamp\n"
            for crypto_entry in crypto_entries:
                timestamp = crypto_entry.timestamp.isoformat()
                output += f"{crypto_entry.rank},{crypto_entry.name},{crypto_entry.value},{timestamp}\n"
            return output
