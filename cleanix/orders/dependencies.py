from typing import Annotated, Tuple

from aiosql.queries import Queries
from asyncpg import Connection
from fastapi import Depends

from orders.exception import PermissionOwnerError
from shared import queries
from users.dependencies import get_user_by_access_token, get_client, get_worker
from users.schema import User, Client, Employee


async def check_order_read_access(
    order_id: int,
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> None:
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())
    if order_dict["client_id"] == user.id or user.is_employee:
        return
    raise PermissionOwnerError


async def check_all_client_orders_read_access(
    user_id: int, user: Annotated[User, Depends(get_user_by_access_token)]
) -> None:
    if not (user_id == user.id or user.is_employee):
        raise PermissionOwnerError


async def check_order_delete_access(
    order_id: int,
    user: Annotated[User, Depends(get_user_by_access_token)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())

    if order_dict["client_id"] == user.id:
        return
    if user.is_employee:
        raw_employee = await db.get_employee_by_user_id(conn, user_id=user.id)
        if raw_employee:
            employee_dict = dict(raw_employee.items())
            if employee_dict["role"] == "MANAGER":
                return

    raise PermissionOwnerError(
        "Orders could be deleted either by cleanix managers or order owners."
    )


async def check_order_modify_access(
    order_id: int,
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    client: Annotated[Client, Depends(get_client)],
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())
    if order_dict["client_id"] == client.id:
        return client
    raise PermissionOwnerError("Orders can only be modified by it's owner.")


async def check_order_assign_access(employee: Annotated[Employee, Depends(get_worker)]):
    return employee


async def check_order_mark_in_process_access(
    employee: Annotated[Employee, Depends(get_worker)]
):
    return employee
