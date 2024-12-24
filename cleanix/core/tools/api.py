from typing import Annotated
from aiosql.queries import Queries
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared import queries
from users.dependencies import get_manager

from .exception import ToolDoesNotExist
from .schema import Tool, ToolInput

tool_router = APIRouter()


@tool_router.post("/", dependencies=[Depends(get_manager)])
async def create_tool(
    payload: ToolInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Tool:
    db, pool = db_factory
    async with pool.acquire() as conn:
        if await db.get_tool_by_name(conn, tool_name=payload.name):
            raise HTTPException(
                detail="Tool with such name already exists.",
                status_code=status.HTTP_409_CONFLICT,
            )
        await db.create_tool(conn, **payload.model_dump())
        raw_tool = await db.get_tool_by_name(conn, tool_name=payload.name)
        return dict(raw_tool.items())


@tool_router.put("/{tool_id}", dependencies=[Depends(get_manager)])
async def modify_tool(
    tool_id: int,
    payload: ToolInput,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> Tool:
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_tool = await db.get_tool_by_id(conn, tool_id=tool_id)
        if not raw_tool:
            raise ToolDoesNotExist
        tool_dict = dict(raw_tool.items())
        if tool_dict["name"] != payload.name:
            # request for item with new name
            if await db.get_tool_by_name(conn, tool_name=payload.name):
                raise HTTPException(
                    detail="Tool with such name already exist.",
                    status_code=status.HTTP_409_CONFLICT,
                )

        tool_dict.update(payload.model_dump())

        await db.update_tool_by_id(conn, tool_id=tool_id, **payload.model_dump())
        new_tool = await db.get_tool_by_id(conn, tool_id=tool_id)
        return dict(new_tool.items())


@tool_router.post("/{tool_id}", dependencies=[Depends(get_manager)])
async def deregister_tool(
    tool_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> None:
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_tool = await db.get_tool_by_id(conn, tool_id=tool_id)
        if not raw_tool:
            raise ToolDoesNotExist
        await db.deregister_tool(conn, tool_id=tool_id)
        response.status_code == status.HTTP_204_NO_CONTENT
        return


@tool_router.get("/")
async def get_tools(
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> list[Tool]:
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_tools = await db.get_tools(conn)
        return [dict(raw_tool.items()) for raw_tool in raw_tools]


@tool_router.get("/{tool_id}")
async def get_tool(
    tool_id: int,
    db_factory: Annotated[tuple[Queries, Connection], Depends(queries)],
) -> Tool:
    db, pool = db_factory
    async with pool.acquire() as conn:
        raw_tool = await db.get_tool_by_id(conn, tool_id=tool_id)
        if raw_tool:
            return dict(raw_tool.items())
        raise ToolDoesNotExist
