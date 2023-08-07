from typing import Any
from typing_extensions import Literal
from pydantic import BaseModel, Field
from pydantic.main import IncEx
from PyObjectId import PyObjectId
from datetime import datetime


class CryptoEntry(BaseModel):
    name: str
    value: float
    rank: int
    timestamp: datetime
