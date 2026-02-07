from __future__ import annotations

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry

_registry = get_instance_registry()


def run_select(query: str, instance_id: str | None = None) -> dict:
    try:
        context = _registry.get(instance_id)
        validated = context.validator.validate(query)
        rows = context.db.execute(validated.query)
        return {"rows": rows, "warnings": validated.warnings}
    except MCPError as exc:
        return exc.to_dict()
