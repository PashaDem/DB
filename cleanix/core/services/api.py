# TODO: rename For... models into Init -> FeedbackInit
# TODO: change update pydantic models: make fields optional
from typing import Annotated

from aiosql.queries import Queries
from asyncpg import Connection
from core.services.exception import ServiceDoesNotExist
from core.services.schema import Service, ServiceInput
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared import queries
from users.dependencies import get_manager

service_router = APIRouter()


@service_router.post("/", dependencies=[Depends(get_manager)])
async def create_service(
    payload: ServiceInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Service:
    db, conn = db_factory
    if await db.get_service_by_name(conn, service_name=payload.name):
        raise HTTPException(
            detail="Service with such name already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )
    await db.create_service(conn, **payload.model_dump())
    raw_service = await db.get_service_by_name(conn, service_name=payload.name)
    return dict(raw_service.items())


@service_router.put("/{service_id}", dependencies=[Depends(get_manager)])
async def modify_service(
    service_id: int,
    payload: ServiceInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Service:
    db, conn = db_factory
    raw_service = await db.get_service_by_id(conn, service_id=service_id)
    if not raw_service:
        raise ServiceDoesNotExist
    service_dict = dict(raw_service.items())
    if service_dict["name"] != payload.name:
        # request for item with new name
        if await db.get_service_by_name(conn, service_name=payload.name):
            raise HTTPException(
                detail="Service with such name already exist.",
                status_code=status.HTTP_409_CONFLICT,
            )

    service_dict.update(payload.model_dump())

    await db.update_service_by_id(conn, service_id=service_id, **payload.model_dump())
    new_service = await db.get_service_by_id(conn, service_id=service_id)
    return dict(new_service.items())


@service_router.post("/{service_id}", dependencies=[Depends(get_manager)])
async def archive_service(
    service_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> None:
    db, conn = db_factory
    await db.archive_service_by_id(conn, service_id=service_id)
    response.status_code == status.HTTP_204_NO_CONTENT


@service_router.get("/")
async def get_services(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> list[Service]:
    db, conn = db_factory
    raw_services = await db.get_services(conn)
    return [dict(raw_service.items()) for raw_service in raw_services]


@service_router.get("/{service_id}")
async def get_service(
    service_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Service:
    db, conn = db_factory
    raw_service = await db.get_service_by_id(conn, service_id=service_id)
    if raw_service:
        return dict(raw_service.items())
    raise ServiceDoesNotExist
