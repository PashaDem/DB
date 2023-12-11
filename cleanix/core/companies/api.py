from typing import Annotated, List, Tuple

from aiosql.queries import Queries
from asyncpg import Connection, Record
from fastapi import APIRouter, Depends, HTTPException, Response, status
from shared import queries
from users.dependencies import get_client
from users.schema import Client

from .exception import CompanyDoesNotExistError
from .schema import Company, CompanyForRegistrationOrUpdate

company_router = APIRouter()


@company_router.post("/")
async def create_company(
    payload: CompanyForRegistrationOrUpdate,
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    company_rec = await db.does_company_exist_for_user_by_id(conn, user_id=client.id)
    company_id = dict(company_rec.items())["company_id"]
    print(company_id)
    if not company_id:
        await db.create_company(conn, user_id=client.id, **payload.model_dump())
        raw_company: Record = await db.get_company_by_user_id(conn, user_id=client.id)
        return dict(raw_company.items())
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "One client can't have several related companies."}


# not tested


@company_router.get("/{company_id}")
async def get_company(
    company_id: int,
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
):
    db, conn = db_factory
    raw_company: Record = await db.get_company_by_id(conn, company_id=company_id)
    if not raw_company:
        raise CompanyDoesNotExistError
    return dict(raw_company.items())


@company_router.get("/")
async def get_companies(
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)]
) -> List[Company]:
    db, conn = db_factory
    raw_company_list = await db.get_companies(conn)
    companies = [dict(raw_company.items()) for raw_company in raw_company_list]
    return companies


@company_router.get("/partners/")
async def get_partner_companies(
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)]
) -> List[Company]:
    db, conn = db_factory
    raw_company_list = await db.get_partner_companies(conn)
    companies = [dict(raw_company.items()) for raw_company in raw_company_list]
    return companies


@company_router.put("/{company_id}")
async def modify_company(
    company_id: int,
    payload: CompanyForRegistrationOrUpdate,
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    client: Annotated[Client, Depends(get_client)],
):
    db, conn = db_factory
    if company_id != client.company_id:
        raise HTTPException(
            detail="User can modify only his company.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    raw_company: Record = await db.get_company_by_id(conn, company_id=company_id)
    company_dict = dict(raw_company.items())
    if payload.name != company_dict["name"]:
        if await db.get_company_by_name(conn, name=payload.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company with such name already exist.",
            )
    for key, value in payload.model_dump().items():
        company_dict[key] = value
    await db.update_company_by_id(conn, **company_dict, company_id=company_id)
    return company_dict


@company_router.post("/unbind_company")
async def unbind_company(
    client: Annotated[Client, Depends(get_client)],
    db_factory: Annotated[Tuple[Queries, Connection], Depends(queries)],
    response: Response,
):
    db, conn = db_factory
    if not client.company_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "Current client has no company to unbind."}
    else:
        await db.unbind_company_by_user_id(conn, user_id=client.id)
        response.status_code = status.HTTP_204_NO_CONTENT
        return
