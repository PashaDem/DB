from exceptions import ModelDoesNotExistError


class ServiceDoesNotExist(ModelDoesNotExistError):
    detail = "Service does not exist."
