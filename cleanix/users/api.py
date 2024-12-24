# TODO: add endpoint for unblocking users
# TODO: move out business logic to repositories
# TODO: try to move the procedures call to aiosql
# TODO: important - catch the exception in verify_password in create_token endpoint
from fastapi import HTTPException
from typing import Annotated, Literal
from enum import StrEnum

from aiosql.queries import Queries
from asyncpg import Connection
from auth.utils import get_password_hash, verify_password
from fastapi import APIRouter, Depends, Response, status
from shared import queries
from fastapi import Request

from .dependencies import get_manager, get_user_by_access_token
from .exception import UsernameIsNotAvailable
from .schema import (
    Employee,
    EmployeeForRegistration,
    PasswordChange,
    User,
    UserForRegistration,
    UserWithoutPassword, RolesEnum, UserInfo, EmployeeForManager,
)

user_router = APIRouter()


@user_router.post("/register", response_model=UserWithoutPassword)
async def register_client(
    user_info: UserForRegistration,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_user = await db.get_user_by_username(conn, username=user_info.username)

        if raw_user:
            raise UsernameIsNotAvailable
        else:
            hashed_password = get_password_hash(user_info.password)
            await conn.execute(
                "CALL insert_full_client($1, $2, $3, $4);",
                user_info.username,
                hashed_password,
                user_info.fullname,
                user_info.contact_phone,
            )

        # check if user was created
        raw_user = await db.get_user_by_username(conn, username=user_info.username)
        raw_user = dict(raw_user.items())

        return dict(raw_user.items())


@user_router.put("/change_password")
async def change_password(
    payload: PasswordChange,
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        if verify_password(payload.old_password, user.password):
            await db.update_password(
                conn, user_id=user.id, new_password=get_password_hash(payload.new_password)
            )
            response.status_code = status.HTTP_204_NO_CONTENT
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"detail": "Invalid old password was provided."}


@user_router.post("/{user_id}/block")
async def block_user(
    user_id: int,
    manager: Annotated[Employee, Depends(get_manager)],
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_user = await db.get_user_by_id(conn, user_id=user_id)
        if raw_user:
            user = User(**dict(raw_user.items()))
            if not user.is_active:
                raise HTTPException(
                    detail="Пользователь уже заблокирован",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if user.id != manager.id:
                await db.block_user_by_id(conn, user.id)
                response.status_code = status.HTTP_204_NO_CONTENT
                return
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "Пользователя с данным id не существует"}


@user_router.post("/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    manager: Annotated[Employee, Depends(get_manager)],
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, pool = db_factory
    async with pool.acquire() as conn:

        raw_user = await db.get_user_by_id(conn, user_id=user_id)
        if raw_user:
            user = User(**dict(raw_user.items()))
            if user.is_active:
                raise HTTPException(
                    detail="Пользователь не заблокирован",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if user.id != manager.id:
                await db.unblock_user_by_id(conn, user.id)
                response.status_code = status.HTTP_204_NO_CONTENT
                return

        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "Пользователя с данным id не существует"}




from pydantic import BaseModel

class CreatedEmployee(BaseModel):
    id: int
    username: str
    fullname: str
    contact_phone: str
    role: Literal['MANAGER', 'EMPLOYEE']
    experience: float


@user_router.post("/register_employee", dependencies=[Depends(get_manager)], response_model=CreatedEmployee)
async def register_employee(
    payload: EmployeeForRegistration,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_user = await db.get_user_by_username(conn, username=payload.username)

        if raw_user:
            raise UsernameIsNotAvailable
        else:
            hashed_password = get_password_hash(payload.password)
            await conn.execute(
                "CALL insert_full_employee($1, $2, $3, $4, $5, $6);",
                payload.username,
                hashed_password,
                payload.fullname,
                payload.contact_phone,
                payload.role,
                payload.experience,
            )

        # check if user was created
        raw_user = await db.get_employee_by_username(conn, username=payload.username)
        raw_user = dict(raw_user.items())
        return dict(raw_user.items())


@user_router.get("/user_info", response_model=UserInfo)
async def get_user_info(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    user: Annotated[User, Depends(get_user_by_access_token)],
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_user_info = await db.get_user_info_by_user_id(conn, user_id=user.id)
        user_dict = dict(raw_user_info.items())

        if not user_dict.get("role", None):
            user_dict['role'] = RolesEnum.CLIENT

        if not user_dict.get("left_feedback", None):
            user_dict['left_feedback'] = False

        return user_dict


@user_router.get("/employees", response_model=list[EmployeeForManager])
async def get_employees(
    request: Request,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    employee: Annotated[Employee, Depends(get_manager)],
):
    db, pool = db_factory
    async with pool.acquire() as conn:
        employees_info = await db.get_employees(conn, current_user_id=employee.id)
        emp_dicts = [dict(emp.items()) for emp in employees_info]
        # удаляем пароли
        [emp_dct.pop("password") for emp_dct in emp_dicts]
        return emp_dicts
