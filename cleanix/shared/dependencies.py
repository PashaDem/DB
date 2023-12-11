from typing import Tuple

import aiosql
from aiosql.queries import Queries
from asyncpg import Connection
from fastapi import Request


class AioSqlDependency:
    def __init__(self, sql_path: str, connector_name: str = "asyncpg"):
        self.queries = aiosql.from_path(sql_path, connector_name)

    def __call__(self, request: Request) -> Tuple[Queries, Connection]:
        return self.queries, request.app.db


queries = AioSqlDependency("/cleanix/sql")
