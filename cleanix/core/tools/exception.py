from exceptions import ModelDoesNotExistError


class ToolDoesNotExist(ModelDoesNotExistError):
    detail = "Tool does not exist."
