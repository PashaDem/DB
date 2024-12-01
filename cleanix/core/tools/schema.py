# TODO: remove is_archived from the model for service creation


from pydantic import BaseModel


class ToolInput(BaseModel):
    description: str
    is_deregistered: bool
    name: str


class Tool(ToolInput):
    id: int
