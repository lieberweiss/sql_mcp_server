from __future__ import annotations

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry
from sql_mcp_server.logging_utils import get_logger

_registry = get_instance_registry()
_logger = get_logger()


def run_select(query: str, instance_id: str | None = None) -> dict:
    try:
        _logger.info(
            "run_select received",
            extra={"instance_id": instance_id or "default", "query": query},
        )
        context = _registry.get(instance_id)
        validated = context.validator.validate(query)
        rows = context.db.execute(validated.query)
        response = {"rows": rows, "warnings": validated.warnings}
        _logger.info(
            "run_select succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "warnings": validated.warnings,
            },
        )
        return response
    except MCPError as exc:
        _logger.warning(
            "run_select failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "message": exc.message,
            },
        )
        return exc.to_dict()


def run_query(query: str, instance_id: str | None = None) -> dict:
    try:
        _logger.info(
            "run_query received",
            extra={"instance_id": instance_id or "default", "query": query},
        )
        context = _registry.get(instance_id)
        validated = context.validator.validate(query)
        rows = context.db.execute(validated.query)
        response = {"rows": rows, "warnings": validated.warnings}
        _logger.info(
            "run_query succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "warnings": validated.warnings,
            },
        )
        return response
    except MCPError as exc:
        _logger.warning(
            "run_query failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "message": exc.message,
            },
        )
        return exc.to_dict()
