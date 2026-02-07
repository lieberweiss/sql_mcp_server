from __future__ import annotations

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry

_registry = get_instance_registry()


def list_tables(instance_id: str | None = None) -> dict:
    try:
        context = _registry.get(instance_id)
        return {"tables": context.db.list_tables()}
    except MCPError as exc:
        return exc.to_dict()


def describe_table(table: str, instance_id: str | None = None) -> dict:
    try:
        context = _registry.get(instance_id)
        return {"columns": context.db.describe_table(table)}
    except MCPError as exc:
        return exc.to_dict()
