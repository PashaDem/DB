from exceptions import ModelDoesNotExistError
from fastapi import status


class CompanyDoesNotExistError(ModelDoesNotExistError):
    detail = "Company with such id does not exist."
    status_code = status.HTTP_400_BAD_REQUEST
