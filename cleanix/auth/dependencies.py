from typing import Annotated, Tuple

import users
from aiosql.queries import Queries
from asyncpg import Connection, Record
from auth.exception import InvalidCredentialsError, BlockedUserError
from auth.schema import TokenData, UserCredentials
from auth.utils import create_access_token, verify_password
from config import auth_config
from fastapi import Depends
from shared import queries


async def check_credentials_and_create_jwt(
    creds: UserCredentials,
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> TokenData:
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_user: Record = await db.get_user_by_username(conn, username=creds.username)
        if raw_user is None:
            raise InvalidCredentialsError
        user: users.schema.User = users.schema.User.model_validate(dict(raw_user.items()))
        if not user:
            raise InvalidCredentialsError

        if not user.is_active:
            raise BlockedUserError

        if verify_password(creds.password, user.password):
            jwt = create_access_token({"sub": str(user.id)})
            return TokenData(
                access_token=jwt, expires_in=auth_config.expiration_time_minutes * 60
            )
        else:
            raise InvalidCredentialsError
