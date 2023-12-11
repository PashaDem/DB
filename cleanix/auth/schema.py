from pydantic import BaseModel


class UserCredentials(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    access_token: str
    expires_in: int
