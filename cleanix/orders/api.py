# TODO: !!! add endpoints for update of the order state

from typing import Annotated
from aiosql.queries import Queries
from asyncpg import Connection, Record
from fastapi import Depends, APIRouter, Response, status, HTTPException

from core.tools.exception import ToolDoesNotExist
from core.transport.exception import TransportDoesNotExist
from shared import queries
from users.dependencies import get_client, get_manager, get_worker
from users.schema import Client, Employee
from .dependencies import (
    check_order_read_access,
    check_order_delete_access,
    check_order_modify_access,
    check_order_assign_access,
    check_order_mark_in_process_access,
)
from .schema import (
    OrderInput,
    Order,
    OrderToSave,
    ServiceIds,
    ServiceId,
    TransportId,
    ToolId, OrderWithServices,
)
from .exception import OrderDoesNotExist

order_router = APIRouter()


#  -----------------------------crud----------------------------------------------------------------


@order_router.post("/", response_model=OrderWithServices)
async def create_order(
    order_data: OrderInput,
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
):
    db, conn = db_factory
    full_payload = order_data.model_dump()
    # получаем услуги
    service_ids = full_payload.pop('services')
    order_to_save = OrderToSave(**(full_payload | {"client_id": client.id}))
    raw_id = await db.insert_full_order(conn, **order_to_save.model_dump())
    await db.increment_order_count(conn, statistics_id=client.statistics_id)
    order_id = dict(raw_id.items())["insert_full_order"]
    [await db.insert_order_service(conn, service_id=service_id, order_id=order_id) for service_id in service_ids]

    services = [dict(raw_obj.items()) for raw_obj in await db.get_services_for_order(conn, order_id)]
    raw_order = await db.get_order_by_id(conn, order_id)

    raw_order = dict(raw_order.items())
    raw_order['services'] = services
    return raw_order


@order_router.get(
    "/client_orders",
    response_model=list[Order],
)
async def get_client_orders(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    client: Annotated[Client, Depends(get_client)],
):
    db, conn = db_factory
    raw_orders = await db.get_orders_by_user_id(conn, user_id=client.id)
    return [dict(raw_order.items()) for raw_order in raw_orders]

@order_router.get(
    "/employee_available_orders",
    response_model=list[Order],
)
async def get_employee_available_orders(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    worker: Annotated[Employee, Depends(get_worker)],
):
    db, conn = db_factory
    orders = await db.get_employee_available_orders(conn)
    return [dict(raw_order.items()) for raw_order in orders]

@order_router.get(
    "/employee_assigned_orders",
    response_model=list[Order],
)
async def get_employee_assigned_orders(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    worker: Annotated[Employee, Depends(get_worker)],
):
    db, conn = db_factory
    orders = await db.get_employee_assigned_orders(conn, worker.id)
    return [dict(raw_order.items()) for raw_order in orders]


@order_router.get(
    "/{order_id}", response_model=Order, dependencies=[Depends(check_order_read_access)]
)
async def get_order(
    order_id: int, db_factory: Annotated[tuple[Queries, Connection], Depends(queries)]
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    return dict(raw_order.items())


@order_router.delete("/{order_id}", dependencies=[Depends(check_order_delete_access)])
async def delete_order(
    order_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())
    if order_dict["status"] == "INQUEUE":
        await db.delete_order_by_id(conn, order_id=order_id)
        await db.decrement_orders_count(conn, client_id=order_dict["client_id"])
        response.status_code = status.HTTP_204_NO_CONTENT
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't delete order with status other than 'INQUEUE'.",
        )


#  -----------------------------services-------------------------------------------------------------
@order_router.post(
    "/{order_id}/add_service", dependencies=[Depends(check_order_modify_access)]
)
async def add_service_to_order(
    order_id: int,
    services_info: ServiceIds,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> None:
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())
    if order_dict["status"] == "INQUEUE":
        await db.append_services_to_order(
            conn, services=services_info.services, order_id=order_id
        )
        response.status_code = status.HTTP_204_NO_CONTENT
        return
    raise HTTPException(
        detail="Can't add service for already paid orders.",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@order_router.post(
    "/{order_id}/remove_service", dependencies=[Depends(check_order_modify_access)]
)
async def remove_service_from_order(
    order_id: int,
    service_info: ServiceId,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    order_dict = dict(raw_order.items())
    if order_dict["status"] == "INQUEUE":
        await db.remove_service_from_order(
            conn, service_id=service_info.service_id, order_id=order_id
        )
        response.status_code = status.HTTP_204_NO_CONTENT
        return
    raise HTTPException(
        detail="Can't remove service for already paid orders.",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


#  ----------------------order lifecycle-------------------------------------------------------------


@order_router.post("/{order_id}/assign_order")
async def assign_order(
    order_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
    employee: Annotated[Employee, Depends(check_order_assign_access)],
) -> None:
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist
    order_dict = dict(raw_order.items())
    if order_dict["status"] == "INQUEUE":
        # сотрудник может принять заказ, только если тот не выполняется еще или не оплачен
        # ( оплата подразумевается после выполнения заказа )
        raw_employee_id_list: list[Record] = await db.get_order_employees_by_order_id(
            conn, order_id=order_id
        )
        employee_id_list: list[int] = [
            raw_id["employee_id"] for raw_id in raw_employee_id_list
        ]
        if employee.id not in employee_id_list:
            await db.assign_order_by_employee_id(
                conn, employee_id=employee.id, order_id=order_id
            )
            response.status_code = status.HTTP_400_BAD_REQUEST
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This employee is already assigned to the order.",
            )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Can't assign paid order or that is processed.",
    )


@order_router.post(
    "/{order_id}/mark_as_in_process",
    response_model=Order,
    dependencies=[Depends(check_order_mark_in_process_access)],
)
async def mark_order_as_in_process(
    order_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
):
    """Заказ помечается, как IN_PROCESS, когда сотрудники начинают оказывать услуги"""
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist
    order_dict = dict(raw_order.items())

    if not order_dict["status"] == "PAID":
        if not order_dict["status"] == "INPROCESS":
            await db.mark_order_as_in_process_by_order_id(conn, order_id=order_id)
            raw_order = await db.get_order_by_id(conn, order_id=order_id)
            return dict(raw_order.items())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't mark order as `in-process`, because it already has the same status.",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Can't mark order as `in-process`, because it is already paid.",
    )


@order_router.post(
    "/{order_id}/mark_as_paid",
    response_model=Order,
    dependencies=[Depends(check_order_mark_in_process_access)],
)
async def mark_order_as_paid(
    order_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
):
    """нельзя пометить как в процессе, потому что если заказ уже оплачен, то что-то менять в нем нельзя"""
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist
    order_dict = dict(raw_order.items())

    if not order_dict["status"] == "PAID":
        if order_dict["status"] == "INPROCESS":
            await db.mark_order_as_paid_by_order_id(conn, order_id=order_id)
            await db.update_total_cost_by_order_id(conn, order_id=order_id)
            raw_order = await db.get_order_by_id(conn, order_id=order_id)
            return dict(raw_order.items())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't mark order as paid, because it hasn't been processed yet.",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Can't mark order as `in-process`, because it is already paid.",
    )


#  -----------------------------transport-------------------------------------------------------------


@order_router.post("/{order_id}/add_transport", dependencies=[Depends(get_manager)])
async def add_transport(
    order_id: int,
    transport_info: TransportId,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist

    does_transport_exist = await db.does_transport_exist(
        conn, transport_id=transport_info.transport_id
    )
    if does_transport_exist:
        transport_ids: list[int] = [
            raw_transport["transport_id"]
            for raw_transport in await db.get_all_order_transports(
                conn, order_id=order_id
            )
        ]
        if transport_info.transport_id not in transport_ids:
            await db.insert_transport_to_order(
                conn, order_id=order_id, transport_id=transport_info.transport_id
            )
            response.status_code = status.HTTP_204_NO_CONTENT
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This transport has already been added to the order.",
        )
    raise TransportDoesNotExist


@order_router.post("/{order_id}/remove_transport", dependencies=[Depends(get_manager)])
async def remove_transport(
    order_id: int,
    transport_info: TransportId,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist

    does_transport_exist = await db.does_transport_exist(
        conn, transport_id=transport_info.transport_id
    )
    if does_transport_exist:
        transport_ids: list[int] = [
            raw_transport["transport_id"]
            for raw_transport in await db.get_all_order_transports(conn, order_id)
        ]
        if transport_info.transport_id in transport_ids:
            await db.remove_transport_from_order(
                conn, order_id=order_id, transport_id=transport_info.transport_id
            )
            response.status_code = status.HTTP_204_NO_CONTENT
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This transport isn't present in order.",
        )
    raise TransportDoesNotExist


# -------------------------------------------tools-----------------------------------------------------------


@order_router.post("/{order_id}/add_tool", dependencies=[Depends(get_manager)])
async def add_tool(
    order_id: int,
    tool_info: ToolId,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist

    does_tool_exist = await db.does_tool_exist(conn, tool_id=tool_info.tool_id)
    if does_tool_exist:
        tool_ids: list[int] = [
            raw_tool["tool_id"]
            for raw_tool in await db.get_all_order_tools(conn, order_id)
        ]
        if tool_info.tool_id not in tool_ids:
            await db.insert_tool_to_order(
                conn, order_id=order_id, tool_id=tool_info.tool_id
            )
            response.status_code = status.HTTP_204_NO_CONTENT
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This tool has already been added to the order.",
        )
    raise ToolDoesNotExist


@order_router.post("/{order_id}/remove_tool", dependencies=[Depends(get_manager)])
async def remove_tool(
    order_id: int,
    tool_info: ToolId,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    raw_order = await db.get_order_by_id(conn, order_id=order_id)
    if not raw_order:
        raise OrderDoesNotExist

    does_tool_exist = await db.does_tool_exist(conn, tool_id=tool_info.tool_id)
    if does_tool_exist:
        tool_ids: list[int] = [
            raw_tool["tool_id"]
            for raw_tool in await db.get_all_order_tools(conn, order_id)
        ]
        if tool_info.tool_id in tool_ids:
            await db.remove_tool_from_order(
                conn, order_id=order_id, tool_id=tool_info.tool_id
            )
            response.status_code = status.HTTP_204_NO_CONTENT
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This tool isn't present in order.",
        )
    raise ToolDoesNotExist
