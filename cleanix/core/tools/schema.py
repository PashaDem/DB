# TODO: remove is_archived from the model for service creation

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    description: str
    is_deregistered: bool
    name: str


class Tool(ToolInput):
    id: int
