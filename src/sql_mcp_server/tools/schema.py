from __future__ import annotations

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry
from sql_mcp_server.logging_utils import get_logger

_registry = get_instance_registry()
_logger = get_logger()


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
                "message": exc.message,
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
        columns = context.db.describe_table(table)
        _logger.info(
            "describe_table succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "table": table,
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
                "message": exc.message,
            },
        )
        return exc.to_dict()
