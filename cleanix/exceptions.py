from fastapi import HTTPException, status


class BaseCleanixException(HTTPException):
    detail = "Base custom exception"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ModelDoesNotExistError(BaseCleanixException):
    status_code = status.HTTP_400_BAD_REQUEST
