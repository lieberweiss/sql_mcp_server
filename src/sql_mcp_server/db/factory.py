from __future__ import annotations

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.db.base import DBClient
from sql_mcp_server.db.mssql import MSSQLClient
from sql_mcp_server.db.mysql import MySQLClient
from sql_mcp_server.db.postgres import PostgresClient
from sql_mcp_server.db.sqlite import SQLiteClient


def _validate_generic_credentials(config: ServerConfig) -> None:
    if not config.host or not config.database or not config.user or not config.password:
        raise RuntimeError(
            "DB_HOST, DB_DATABASE, DB_USER and DB_PASSWORD must be set for this provider"
        )


def create_db_client(config: ServerConfig) -> DBClient:
    if config.provider == "sqlite":
        return SQLiteClient(config)

    if config.provider == "postgres":
        _validate_generic_credentials(config)
        return PostgresClient(config)

    if config.provider == "mysql":
        _validate_generic_credentials(config)
        return MySQLClient(config)

    if config.provider == "mssql":
        _validate_generic_credentials(config)
        return MSSQLClient(config)

    raise RuntimeError(f"Unsupported DB_PROVIDER: {config.provider}")
