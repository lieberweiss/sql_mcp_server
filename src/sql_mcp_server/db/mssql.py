from __future__ import annotations

import os
from typing import Any

import pyodbc

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.db.base import DBClient


class MSSQLClient(DBClient):
    def __init__(self, config: ServerConfig) -> None:
        self._config = config
        driver = self._resolve_driver()
        trust_server_certificate = config.mssql_trust_server_certificate
        trust_server_certificate_str = "yes" if trust_server_certificate else "no"
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={config.host},{config.port or 1433};"
            f"DATABASE={config.database};"
            f"UID={config.user};PWD={config.password};"
            f"Encrypt=yes;TrustServerCertificate={trust_server_certificate_str};"
        )
        self._conn = pyodbc.connect(conn_str, timeout=config.query_timeout)
        self._statement_timeout_seconds = config.statement_timeout_seconds

    def _resolve_driver(self) -> str:
        configured_driver = self._config.mssql_odbc_driver or os.getenv("DB_MSSQL_ODBC_DRIVER")
        if configured_driver:
            return configured_driver

        installed = {d.lower() for d in pyodbc.drivers()}
        preferred = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "SQL Server",
        ]
        for driver in preferred:
            if driver.lower() in installed:
                return driver

        return "ODBC Driver 18 for SQL Server"

    def execute(self, query: str) -> list[dict[str, Any]]:
        cur = self._conn.cursor()
        if self._statement_timeout_seconds is not None:
            cur.timeout = self._statement_timeout_seconds
        cur.execute(query)
        columns = [c[0] for c in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def list_tables(self) -> list[str]:
        rows = self.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
        )
        return [r["TABLE_NAME"] for r in rows]

    def describe_table(self, table: str) -> list[dict[str, Any]]:
        return self.execute(
            "\n".join(
                [
                    "SELECT COLUMN_NAME, DATA_TYPE",
                    "FROM INFORMATION_SCHEMA.COLUMNS",
                    f"WHERE TABLE_NAME = '{table}'",
                ]
            )
        )
