from exceptions import BaseCleanixException
from fastapi import status


class InvalidCredentialsError(BaseCleanixException):
    detail = "Mistake in username or password"
    status_code = status.HTTP_400_BAD_REQUEST


class BadToken(BaseCleanixException):
    detail = "The access token is invalid."
    status_code = status.HTTP_400_BAD_REQUEST


class TokenExpiredError(BaseCleanixException):
    detail = "Got expired token."
    status_code = status.HTTP_400_BAD_REQUEST
