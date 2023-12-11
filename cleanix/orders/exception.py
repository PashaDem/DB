from exceptions import BaseCleanixException, ModelDoesNotExistError

from fastapi import status


class PermissionOwnerError(BaseCleanixException):
    detail = "The order can be viewed either by cleanix employees or order's owner"
    status_code = status.HTTP_403_FORBIDDEN


class OrderDoesNotExist(ModelDoesNotExistError):
    detail = "Order does not exist."

