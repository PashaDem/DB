from typing import List

from pydantic import BaseModel
from datetime import date

from core.services.schema import Service


class OrderInput(BaseModel):
    address: str
    clean_date: date
    services: list[int]


class OrderToSave(BaseModel):
    client_id: int
    address: str
    clean_date: date
    status: str = "INQUEUE"



class Order(OrderToSave):
    id: int
    contract_id: int
    username: str
    services: list[Service]


class OrderWithServices(Order):
    services: list[Service]


class ServiceIds(BaseModel):
    services: list[int]


class ServiceId(BaseModel):
    service_id: int


class TransportId(BaseModel):
    transport_id: int


class ToolId(BaseModel):
    tool_id: int
