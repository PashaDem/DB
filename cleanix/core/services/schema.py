# TODO: remove is_archived from the model for service creation

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ServiceInput(BaseModel):
    type: str
    description: str
    price: Annotated[Decimal, Field(decimal_places=2)]
    is_archived: bool
    name: str


class Service(ServiceInput):
    id: int
