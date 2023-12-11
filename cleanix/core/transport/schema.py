from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class TransportInput(BaseModel):
    description: str
    is_deregistered: bool
    brand: str
    name: str


class Transport(TransportInput):
    id: int
