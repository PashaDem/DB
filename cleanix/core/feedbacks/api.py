# TODO: rename For... models into Init -> FeedbackInit
# TODO: change update pydantic models: make fields optional
from datetime import date
from typing import Annotated, List, Tuple

from aiosql.queries import Queries
from asyncpg import Connection
from core.feedbacks.exception import FeedbackDoesNotExist
from core.feedbacks.schema import Feedback, FeedbackInit, FeedbackInput
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared import queries
from users.dependencies import get_client
from users.schema import Client

feedback_router = APIRouter()


@feedback_router.post("/")
async def create_feedback(
    payload: FeedbackInput,
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> Feedback:
    db, conn = db_factory

    has_feedback = await db.get_feedback_by_client_id(conn, client_id=client.id)
    if has_feedback:
        raise HTTPException(
            detail="This user has already commented the cleanix service.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    additional_data = {
        "client_id": client.id,
        "create_at": date.today(),
    }
    feedback = FeedbackInit(**(payload.model_dump() | additional_data))
    await db.insert_feedback(conn, **feedback.model_dump())
    await db.mark_feedback_as_left(conn, statistics_id=client.statistics_id)
    raw_feedback = await db.get_feedback_by_client_id(conn, client_id=client.id)
    return dict(raw_feedback.items())


@feedback_router.put("/")
async def modify_feedback(
    payload: FeedbackInput,
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> Feedback:
    db, conn = db_factory
    raw_feed = await db.get_feedback_by_client_id(conn, client_id=client.id)
    if not raw_feed:
        raise FeedbackDoesNotExist
    dict_feed = dict(raw_feed.items())
    dict_feed.update(payload.model_dump())
    await db.update_feedback_by_id(conn, **dict_feed)
    new_feedback = await db.get_feedback_by_client_id(conn, client_id=client.id)
    return dict(new_feedback.items())


@feedback_router.delete("/")
async def remove_feedback(
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    response: Response,
) -> None:
    db, conn = db_factory
    raw_feed = await db.get_feedback_by_client_id(conn, client_id=client.id)
    if not raw_feed:
        raise FeedbackDoesNotExist
    await db.delete_feedback_by_client_id(conn, client_id=client.id)
    await db.mark_feedback_as_deleted(conn, statistics_id=client.statistics_id)
    response.status_code = status.HTTP_204_NO_CONTENT
    return


@feedback_router.get("/")
async def get_feedbacks(
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> List[Feedback]:
    db, conn = db_factory
    raw_feeds = await db.get_feedbacks(conn)
    return [dict(raw_feed.items()) for raw_feed in raw_feeds]


@feedback_router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: int,
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
) -> Feedback:
    db, conn = db_factory
    raw_feedback = await db.get_feedback_by_id(conn, feedback_id=feedback_id)
    if raw_feedback:
        return dict(raw_feedback.items())
    raise FeedbackDoesNotExist
