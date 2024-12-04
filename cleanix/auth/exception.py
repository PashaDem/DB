from exceptions import BaseCleanixException
from fastapi import status


class InvalidCredentialsError(BaseCleanixException):
    detail = "Ошибка в пароле или имени пользователя"
    status_code = status.HTTP_400_BAD_REQUEST


class BadToken(BaseCleanixException):
    detail = "Некорректный авторизационный токен"
    status_code = status.HTTP_400_BAD_REQUEST


class TokenExpiredError(BaseCleanixException):
    detail = "Срок действия токена истек"
    status_code = status.HTTP_400_BAD_REQUEST


class BlockedUserError(BaseCleanixException):
    detail = "Пользователь заблокирован"
    status_code = status.HTTP_403_FORBIDDEN
