from pydantic import BaseModel


class TransportInput(BaseModel):
    description: str
    is_deregistered: bool
    brand: str
    name: str


class Transport(TransportInput):
    id: int
