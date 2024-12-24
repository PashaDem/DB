from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from auth import auth_router
from config import AppConfig
from core.companies import company_router
from core.feedbacks import feedback_router
from core.services import service_router
from core.tools import tool_router
from fastapi import FastAPI
from users import user_router
from core.transport import transport_router
from orders import order_router
from fastapi.middleware.cors import CORSMiddleware

# lifespan
@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator:
    app_config = AppConfig()
    app.db = await asyncpg.create_pool(
        min_size=10,
        max_size=100,
        host=app_config.postgres_host,
        port=app_config.postgres_port,
        user=app_config.postgres_user,
        password=app_config.postgres_password,
        database=app_config.postgres_db,
    )
    with open(app_config.sql_init_path, "r") as queries:
        await app.db.execute(queries.read())
    yield
    await app.db.close()


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(company_router, prefix="/companies")
app.include_router(feedback_router, prefix="/feedbacks")
app.include_router(service_router, prefix="/services")
app.include_router(tool_router, prefix="/tools")
app.include_router(transport_router, prefix="/transport")
app.include_router(order_router, prefix="/orders")
