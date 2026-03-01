from __future__ import annotations

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import InstanceContext, get_instance_registry
from sql_mcp_server.logging_utils import get_logger

_registry = get_instance_registry()
_logger = get_logger()


def _normalize_table(table: str) -> str:
    normalized = table.strip()
    if not normalized:
        raise MCPError(
            "Table name is empty",
            hint="Provide a table identifier",
            error_type="InvalidTable",
        )
    return normalized


def _assert_table_allowed(
    table: str, context: InstanceContext, known_tables: list[str] | None = None
) -> str:
    normalized = _normalize_table(table)
    lower_normalized = normalized.lower()

    allowed = context.config.allowed_tables
    if allowed and lower_normalized not in allowed:
        raise MCPError(
            f"Access denied to table: {normalized}",
            hint=f"Allowed tables: {', '.join(sorted(allowed))}",
            error_type="TableNotAllowed",
        )

    catalog = {t.lower(): t for t in (known_tables or [])}
    if catalog and lower_normalized not in catalog:
        raise MCPError(
            f"Unknown table: {normalized}",
            hint="Call list_tables to discover available tables",
            error_type="UnknownTable",
        )

    return catalog.get(lower_normalized, normalized)


def list_tables(instance_id: str | None = None) -> dict:
    try:
        _logger.info(
            "list_tables received",
            extra={"instance_id": instance_id or "default"},
        )
        context = _registry.get(instance_id)
        tables = context.db.list_tables()
        _logger.info(
            "list_tables succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "table_count": len(tables),
            },
        )
        return {"tables": tables}
    except MCPError as exc:
        _logger.warning(
            "list_tables failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "error_message": exc.message,
            },
        )
        return exc.to_dict()


def describe_table(table: str, instance_id: str | None = None) -> dict:
    try:
        _logger.info(
            "describe_table received",
            extra={"instance_id": instance_id or "default", "table": table},
        )
        context = _registry.get(instance_id)
        table_names = context.db.list_tables()
        normalized = _assert_table_allowed(table, context, table_names)
        columns = context.db.describe_table(normalized)
        _logger.info(
            "describe_table succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "table": normalized,
                "column_count": len(columns),
            },
        )
        return {"columns": columns}
    except MCPError as exc:
        _logger.warning(
            "describe_table failed",
            extra={
                "instance_id": instance_id or "default",
                "table": table,
                "error_type": exc.error_type,
                "error_message": exc.message,
            },
        )
        return exc.to_dict()
