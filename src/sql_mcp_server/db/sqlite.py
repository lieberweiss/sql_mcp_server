from __future__ import annotations

import sqlite3
import time
from typing import Any

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.db.base import DBClient


class SQLiteClient(DBClient):
    def __init__(self, config: ServerConfig) -> None:
        self._config = config
        self._conn = sqlite3.connect(config.sqlite_path, timeout=config.query_timeout)
        self._conn.row_factory = sqlite3.Row
        self._statement_timeout_seconds = config.statement_timeout_seconds
        self._current_query_deadline: float | None = None
        if self._statement_timeout_seconds:
            # Abort long-running queries by polling SQLite's progress handler.
            self._conn.set_progress_handler(self._progress_handler, 1000)

    def _progress_handler(self) -> int:
        if self._current_query_deadline is None:
            return 0
        if time.monotonic() >= self._current_query_deadline:
            return 1
        return 0

    def execute(self, query: str) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        try:
            if self._statement_timeout_seconds:
                self._current_query_deadline = (
                    time.monotonic() + self._statement_timeout_seconds
                )
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            if self._statement_timeout_seconds:
                self._current_query_deadline = None

    def list_tables(self) -> list[str]:
        rows = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [r["name"] for r in rows]

    def describe_table(self, table: str) -> list[dict[str, Any]]:
        return self.execute(f"PRAGMA table_info({table})")
