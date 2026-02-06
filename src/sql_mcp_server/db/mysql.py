from __future__ import annotations

from typing import Any

import pymysql

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


class MySQLClient(DBClient):
    def __init__(self) -> None:
        self._conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT or 3306,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            connect_timeout=DB_QUERY_TIMEOUT,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self._configure_statement_timeout()

    def _configure_statement_timeout(self) -> None:
        if DB_STATEMENT_TIMEOUT_MS <= 0:
            return

        with self._conn.cursor() as cur:
            cur.execute(
                "SET SESSION MAX_EXECUTION_TIME = %s",
                (DB_STATEMENT_TIMEOUT_MS,),
            )
        self._conn.commit()

    def execute(self, query: str) -> list[dict[str, Any]]:
        with self._conn.cursor() as cur:
            cur.execute(query)
            return list(cur.fetchall())

    def list_tables(self) -> list[str]:
        rows = self.execute("SHOW TABLES")
        return [list(r.values())[0] for r in rows]

    def describe_table(self, table: str) -> list[dict[str, Any]]:
        return self.execute(f"DESCRIBE {table}")
