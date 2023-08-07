from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class CryptoEntry(BaseModel):
    name: str
    value: float
    rank: int
    timestamp: datetime


class OutputFormat(Enum):
    JSON = "JSON"
    CSV = "CSV"
