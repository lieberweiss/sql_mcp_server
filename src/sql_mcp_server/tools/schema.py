from __future__ import annotations

from sql_mcp_server.db.factory import get_db_client

_db = get_db_client()


def list_tables() -> dict:
    return {"tables": _db.list_tables()}


def describe_table(table: str) -> dict:
    return {"columns": _db.describe_table(table)}
