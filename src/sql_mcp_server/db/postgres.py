from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras

from sql_mcp_server.config import (
    DB_DATABASE,
    DB_HOST,
    DB_PASSWORD,
    DB_PORT,
    DB_QUERY_TIMEOUT,
    DB_STATEMENT_TIMEOUT_MS,
    DB_USER,
)
from sql_mcp_server.db.base import DBClient


class PostgresClient(DBClient):
    def __init__(self) -> None:
        self._conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT or 5432,
            dbname=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=DB_QUERY_TIMEOUT,
        )
        self._configure_statement_timeout()

    def _configure_statement_timeout(self) -> None:
        if DB_STATEMENT_TIMEOUT_MS <= 0:
            return

        with self._conn.cursor() as cur:
            cur.execute("SET statement_timeout = %s", (DB_STATEMENT_TIMEOUT_MS,))
        self._conn.commit()

    def execute(self, query: str) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return list(cur.fetchall())

    def list_tables(self) -> list[str]:
        rows = self.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        return [r["table_name"] for r in rows]

    def describe_table(self, table: str) -> list[dict[str, Any]]:
        return self.execute(
            "\n".join(
                [
                    "SELECT column_name, data_type",
                    "FROM information_schema.columns",
                    f"WHERE table_name = '{table}'",
                ]
            )
        )
