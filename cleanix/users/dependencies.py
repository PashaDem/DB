import logging
from typing import Annotated, Tuple

from aiosql.queries import Queries
from asyncpg import Connection, Record
from auth.exception import BadToken, BlockedUserError
from config import auth_config
from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from shared import queries
from starlette import status
from users.exception import (
    PermissionClientError,
    PermissionManagerError,
    PermissionWorkerError,
)
from users.schema import Client, Employee, User


async def get_user_by_access_token(
    authorization: Annotated[str | None, Header()],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> User:
    db, pool = db_factory
    async with pool.acquire() as conn:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token wasn't provided.",
            )
        try:
            token = authorization.rstrip().split()[1]
            payload = jwt.decode(
                token, auth_config.secret_key, algorithms=[auth_config.algorithm]
            )
            user_id = int(payload.get("sub"))
            if user_id is None:
                raise BadToken
        except JWTError as e:
            logging.exception(e)
            raise BadToken
        except Exception as e:
            logging.exception(e)
            raise BadToken

        raw_user: Record = await db.get_user_by_id(conn, user_id)
        if not raw_user:
            raise BadToken

        user = dict(raw_user.items())
        if not user['is_active']:
            raise BlockedUserError

        return User.model_validate(dict(raw_user.items()))


async def get_manager(
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> Employee:
    if user.is_employee:
        db, pool = db_factory
        async with pool.acquire() as conn:
            raw_employee = await db.get_employee_by_user_id(conn, user_id=user.id)
            if not raw_employee:
                raise HTTPException(
                    detail="Ручка только для администраторов сервиса",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            employee = dict(raw_employee.items())
            employee.update(**user.model_dump())
            employee = Employee(**employee)
            if employee.role == "MANAGER":
                return employee
    raise PermissionManagerError


async def get_client(
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> Client:
    if not user.is_employee:
        db, pool = db_factory
        async with pool.acquire() as conn:
            raw_client = await db.get_client_by_user_id(conn, user_id=user.id)
            if not raw_client:
                raise HTTPException(
                    detail="Удалить свой отзыв может только клиент сервиса",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            client_dict = dict(raw_client.items())
            client_dict.update(user.model_dump())
            client: Client = Client(**client_dict)
            return client
    raise PermissionClientError


async def get_worker(
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> Employee:
    if user.is_employee:
        db, pool = db_factory
        async with pool.acquire() as conn:
            raw_employee = await db.get_employee_by_user_id(conn, user_id=user.id)
            if not raw_employee:
                raise HTTPException(
                    detail="Ручка только для сотрудников сервиса",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            employee = dict(raw_employee.items())
            employee.update(**user.model_dump())
            employee = Employee(**employee)
            if employee.role == "EMPLOYEE":
                return employee
    raise PermissionWorkerError
