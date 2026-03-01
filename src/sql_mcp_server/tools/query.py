from __future__ import annotations

import time

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry
from sql_mcp_server.logging_utils import (
    get_logger,
    get_query_logger,
    render_query_logging_metadata,
)

_registry = get_instance_registry()
_logger = get_logger()
_query_logger = get_query_logger()


def run_select(query: str, instance_id: str | None = None) -> dict:
    return _execute_query(query, instance_id, expected_select=True)


def run_query(query: str, instance_id: str | None = None) -> dict:
    return _execute_query(query, instance_id, expected_select=False)


def _execute_query(
    query: str, instance_id: str | None, expected_select: bool
) -> dict:
    started = time.monotonic()
    tool_name = "run_select" if expected_select else "run_query"
    try:
        _logger.info(
            f"{tool_name} received",
            extra={"instance_id": instance_id or "default"},
        )
        _query_logger.info(
            "query received",
            extra={
                "instance_id": instance_id or "default",
                **render_query_logging_metadata(query),
            },
        )
        context = _registry.get(instance_id)
        validated = context.validator.validate(query)
        if expected_select and not validated.is_select:
            raise MCPError(
                "Only SELECT statements are allowed in run_select",
                hint="Use run_query for write operations",
                error_type="SelectOnlyTool",
            )
        rows = context.db.execute(validated.query)
        response = {"rows": rows, "warnings": validated.warnings}
        _logger.info(
            f"{tool_name} succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "warnings": validated.warnings,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.info(
            "query succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
                **render_query_logging_metadata(query),
            },
        )
        return response
    except MCPError as exc:
        _logger.warning(
            f"{tool_name} failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "error_message": exc.message,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.warning(
            "query failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "error_message": exc.message,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
                **render_query_logging_metadata(query),
            },
        )
        return exc.to_dict()
    except BaseException:
        _logger.exception(
            f"{tool_name} crashed",
            extra={
                "instance_id": instance_id or "default",
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.exception(
            "query crashed",
            extra={
                "instance_id": instance_id or "default",
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
                **render_query_logging_metadata(query),
            },
        )
        raise
