from exceptions import BaseCleanixException
from fastapi import status


class UsernameIsNotAvailable(BaseCleanixException):
    detail = "The username you provided is already taken."
    status_code = status.HTTP_409_CONFLICT


class PermissionManagerError(BaseCleanixException):
    detail = "This action can be performed only by Cleanix managers."
    status_code = status.HTTP_403_FORBIDDEN


class PermissionWorkerError(BaseCleanixException):
    detail = "This action can be performed only by Cleanix workers."
    status_code = status.HTTP_403_FORBIDDEN


class PermissionClientError(BaseCleanixException):
    detail = "This action can be performed only by Cleanix clients."
    status_code = status.HTTP_403_FORBIDDEN
