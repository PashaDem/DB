from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field

# TODO: add contact phone validation


class UserForRegistration(BaseModel):
    username: str
    password: str
    fullname: str
    contact_phone: str


class UserWithoutPassword(BaseModel):
    id: int
    username: str
    fullname: str
    contact_phone: str
    is_employee: bool
    is_active: bool


class User(UserWithoutPassword):
    password: str


class EmployeeForRegistration(UserForRegistration):
    role: Literal["EMPLOYEE", "MANAGER"]
    experience: Annotated[Decimal, Field(decimal_places=2)]


class Employee(EmployeeForRegistration, User):
    role: Literal["EMPLOYEE", "MANAGER"]
    experience: Annotated[Decimal, Field(decimal_places=2)]


class EmployeeForManager(UserWithoutPassword):
    role: Literal["EMPLOYEE", "MANAGER"]
    experience: Annotated[Decimal, Field(decimal_places=2)]

class Client(User):
    company_id: Optional[int]
    statistics_id: int


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class RolesEnum(StrEnum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    CLIENT = "CLIENT"

class ClientStatistics(BaseModel):
    orders_count: int
    total_price: float
    left_feedback: bool

class UserInfo(BaseModel):
    id: int
    role: RolesEnum
    fullname: str
    contact_phone: str
    username: str
    is_active: bool
    is_employee: bool
    left_feedback: bool
    statistics: ClientStatistics | None = None
