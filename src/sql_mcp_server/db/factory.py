from __future__ import annotations

from sql_mcp_server.config import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_PROVIDER, DB_USER
from sql_mcp_server.db.base import DBClient
from sql_mcp_server.db.mssql import MSSQLClient
from sql_mcp_server.db.mysql import MySQLClient
from sql_mcp_server.db.postgres import PostgresClient
from sql_mcp_server.db.sqlite import SQLiteClient


def _validate_generic_credentials() -> None:
    if not DB_HOST or not DB_DATABASE or not DB_USER or not DB_PASSWORD:
        raise RuntimeError(
            "DB_HOST, DB_DATABASE, DB_USER and DB_PASSWORD must be set for this provider"
        )


def get_db_client() -> DBClient:
    if DB_PROVIDER == "sqlite":
        return SQLiteClient()

    if DB_PROVIDER == "postgres":
        _validate_generic_credentials()
        return PostgresClient()

    if DB_PROVIDER == "mysql":
        _validate_generic_credentials()
        return MySQLClient()

    if DB_PROVIDER == "mssql":
        _validate_generic_credentials()
        return MSSQLClient()

    raise RuntimeError(f"Unsupported DB_PROVIDER: {DB_PROVIDER}")
