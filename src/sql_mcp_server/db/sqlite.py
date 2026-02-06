from __future__ import annotations

import sqlite3
from typing import Any

from sql_mcp_server.config import DB_QUERY_TIMEOUT, SQLITE_PATH
from sql_mcp_server.db.base import DBClient


class SQLiteClient(DBClient):
    def __init__(self) -> None:
        self._conn = sqlite3.connect(SQLITE_PATH, timeout=DB_QUERY_TIMEOUT)
        self._conn.row_factory = sqlite3.Row

    def execute(self, query: str) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def list_tables(self) -> list[str]:
        rows = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [r["name"] for r in rows]

    def describe_table(self, table: str) -> list[dict[str, Any]]:
        return self.execute(f"PRAGMA table_info({table})")
