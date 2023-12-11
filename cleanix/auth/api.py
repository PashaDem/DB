# TODO: dont create token for not active users (dont authorize)

from typing import Annotated

from fastapi import APIRouter, Depends

from .dependencies import check_credentials_and_create_jwt
from .schema import TokenData

auth_router = APIRouter()


@auth_router.post("/token", response_model=TokenData)
async def create_jwt_token(
    token: Annotated[TokenData, Depends(check_credentials_and_create_jwt)]
):
    return token
