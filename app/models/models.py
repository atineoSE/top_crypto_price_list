from pydantic import BaseModel, model_serializer
from enum import Enum
from datetime import datetime
import json
from typing import Any


class CryptoEntry(BaseModel):
    """A model to represent a crypto entry.

    Fields:
        name: The name of the crypto.
        value: The value of the crypto in USD.
        rank: The rank of the crypto, starting with 1 for the top coin.
        timestamp: The timestamp corresponding to the value sampled.
    """
    name: str
    value: float
    rank: int
    timestamp: datetime

    @model_serializer
    def serialize(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "rank": self.rank,
            "timestamp": self.timestamp.isoformat()
        }


class OutputFormat(Enum):
    """Output format for the crypto entries.

    It can be either JSON or CSV.
    """
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
