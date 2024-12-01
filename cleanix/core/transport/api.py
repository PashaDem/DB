from typing import Annotated
from aiosql.queries import Queries
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared import queries
from users.dependencies import get_manager

from .exception import TransportDoesNotExist
from .schema import TransportInput, Transport

transport_router = APIRouter()


@transport_router.post("/", dependencies=[Depends(get_manager)])
async def create_transport(
    payload: TransportInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Transport:
    db, conn = db_factory
    if await db.get_transport_by_name(conn, transport_name=payload.name):
        raise HTTPException(
            detail="Transport with such name already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )
    await db.create_transport(conn, **payload.model_dump())
    raw_transport = await db.get_transport_by_name(conn, transport_name=payload.name)
    return dict(raw_transport.items())


@transport_router.put("/{transport_id}", dependencies=[Depends(get_manager)])
async def modify_transport(
    transport_id: int,
    payload: TransportInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Transport:
    db, conn = db_factory
    raw_transport = await db.get_transport_by_id(conn, transport_id=transport_id)
    if not raw_transport:
        raise TransportDoesNotExist
    transport_dict = dict(raw_transport.items())
    if transport_dict["name"] != payload.name:
        # request for item with new name
        if await db.get_transport_by_name(conn, transport_name=payload.name):
            raise HTTPException(
                detail="Transport with such name already exist.",
                status_code=status.HTTP_409_CONFLICT,
            )

    transport_dict.update(payload.model_dump())

    await db.update_transport_by_id(
        conn, transport_id=transport_id, **payload.model_dump()
    )
    new_transport = await db.get_transport_by_id(conn, transport_id=transport_id)
    return dict(new_transport.items())


@transport_router.post("/{transport_id}", dependencies=[Depends(get_manager)])
async def deregister_transport(
    transport_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> None:
    db, conn = db_factory
    raw_transport = await db.get_transport_by_id(conn, transport_id=transport_id)
    if not raw_transport:
        raise TransportDoesNotExist
    await db.deregister_transport(conn, transport_id=transport_id)
    response.status_code == status.HTTP_204_NO_CONTENT
    return


@transport_router.get("/")
async def get_transports(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> list[Transport]:
    db, conn = db_factory
    raw_transports = await db.get_transports(conn)
    return [dict(raw_transport.items()) for raw_transport in raw_transports]


@transport_router.get("/{transport_id}")
async def get_transport(
    transport_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Transport:
    db, conn = db_factory
    raw_transport = await db.get_transport_by_id(conn, transport_id=transport_id)
    if raw_transport:
        return dict(raw_transport.items())
    raise TransportDoesNotExist
