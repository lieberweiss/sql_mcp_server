from __future__ import annotations

import unittest

from sql_mcp_server.config import ServerConfig
from sql_mcp_server.errors import MCPError
from sql_mcp_server.middleware.sql_validator import SQLValidator


def _make_config(**overrides) -> ServerConfig:
    base = dict(
        instance_id="default",
        provider="sqlite",
        host=None,
        port=None,
        user=None,
        password=None,
        database=None,
        sqlite_path=":memory:",
        read_only=True,
        max_rows=100,
        query_timeout=10,
        statement_timeout_ms=10_000,
        allowed_tables={"users"},
        server_name="sql-mcp-server",
        mssql_odbc_driver=None,
        mssql_trust_server_certificate=False,
        allow_alter=False,
        allow_drop=False,
    )
    base.update(overrides)
    return ServerConfig(**base)


class SQLValidatorTableTests(unittest.TestCase):
    def test_validate_allows_allowed_table(self) -> None:
        validator = SQLValidator(_make_config())

        result = validator.validate("SELECT * FROM users u WHERE u.id = 1")

        self.assertTrue(result.is_select)
        self.assertEqual(result.warnings, [])

    def test_validate_blocks_disallowed_join_table(self) -> None:
        validator = SQLValidator(_make_config())

        with self.assertRaises(MCPError) as ctx:
            validator.validate(
                "SELECT * FROM users u JOIN accounts a ON a.user_id = u.id"
            )

        self.assertEqual(ctx.exception.error_type, "TableNotAllowed")


if __name__ == "__main__":
    unittest.main()
