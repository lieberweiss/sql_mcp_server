from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.db.base import DBClient


class PostgresClient(DBClient):
    def __init__(self, config: ServerConfig) -> None:
        self._config = config
        self._conn = psycopg2.connect(
            host=config.host,
            port=config.port or 5432,
            dbname=config.database,
            user=config.user,
            password=config.password,
            connect_timeout=config.query_timeout,
        )
        self._configure_statement_timeout()

    def _configure_statement_timeout(self) -> None:
        if self._config.statement_timeout_ms <= 0:
            return

        with self._conn.cursor() as cur:
            cur.execute("SET statement_timeout = %s", (self._config.statement_timeout_ms,))
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
