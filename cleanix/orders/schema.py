from typing import List

from pydantic import BaseModel
from datetime import date


class OrderInput(BaseModel):
    address: str
    clean_date: date


class OrderToSave(OrderInput):
    client_id: int
    status: str = "INQUEUE"


class Order(OrderToSave):
    id: int
    contract_id: int


class ServiceIds(BaseModel):
    services: List[int]


class ServiceId(BaseModel):
    service_id: int


class TransportId(BaseModel):
    transport_id: int


class ToolId(BaseModel):
    tool_id: int
