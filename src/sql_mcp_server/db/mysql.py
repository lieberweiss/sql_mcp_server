from __future__ import annotations

from typing import Any

import pymysql

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.db.base import DBClient


class MySQLClient(DBClient):
    def __init__(self, config: ServerConfig) -> None:
        self._config = config
        self._conn = pymysql.connect(
            host=config.host,
            port=config.port or 3306,
            user=config.user,
            password=config.password,
            database=config.database,
            connect_timeout=config.query_timeout,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self._configure_statement_timeout()

    def _configure_statement_timeout(self) -> None:
        if self._config.statement_timeout_ms <= 0:
            return

        with self._conn.cursor() as cur:
            cur.execute(
                "SET SESSION MAX_EXECUTION_TIME = %s",
                (self._config.statement_timeout_ms,),
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
