from __future__ import annotations

from sql_mcp_server.db.factory import get_db_client
from sql_mcp_server.errors import MCPError
from sql_mcp_server.middleware.sql_validator import SQLValidator

_db = get_db_client()
_validator = SQLValidator()


def run_select(query: str) -> dict:
    try:
        validated = _validator.validate(query)
        rows = _db.execute(validated.query)
        return {"rows": rows, "warnings": validated.warnings}
    except MCPError as exc:
        return exc.to_dict()
