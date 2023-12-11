# TODO: add unique contraint to one to one connection between user and company

from pydantic import BaseModel


class CompanyForRegistrationOrUpdate(BaseModel):
    name: str
    type: str
    show_in_partners: bool


class Company(CompanyForRegistrationOrUpdate):
    id: int
