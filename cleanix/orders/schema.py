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


class Tool(BaseModel):
    id: int
    name: str
    description: str
    is_deregistered: bool


class Transport(BaseModel):
    id: int
    name: str
    brand: str
    description: str
    is_deregistered: bool


class Order(OrderToSave):
    id: int
    contract_id: int
    username: str
    services: list[Service]


class OrderWithoutServices(OrderToSave):
    id: int
    contract_id: int
    username: str


class OrderWithToolsAndTransport(OrderToSave):
    id: int
    contract_id: int
    username: str
    services: list[Service]
    tools: list[Tool]
    transports: list[Transport]

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
