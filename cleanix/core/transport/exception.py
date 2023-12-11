from exceptions import ModelDoesNotExistError


class TransportDoesNotExist(ModelDoesNotExistError):
    detail = "Transport does not exist."
