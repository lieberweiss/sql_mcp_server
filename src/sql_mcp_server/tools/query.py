from __future__ import annotations

import time

from sql_mcp_server.errors import MCPError
from sql_mcp_server.instances import get_instance_registry
from sql_mcp_server.logging_utils import get_logger, get_query_logger

_registry = get_instance_registry()
_logger = get_logger()
_query_logger = get_query_logger()


def run_select(query: str, instance_id: str | None = None) -> dict:
    started = time.monotonic()
    try:
        _logger.info(
            "run_select received",
            extra={"instance_id": instance_id or "default"},
        )
        _query_logger.info(
            "query received",
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
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.info(
            "query succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
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
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.warning(
            "query failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "message": exc.message,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        return exc.to_dict()
    except BaseException:
        _logger.exception(
            "run_select crashed",
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
            },
        )
        raise


def run_query(query: str, instance_id: str | None = None) -> dict:
    started = time.monotonic()
    try:
        _logger.info(
            "run_query received",
            extra={"instance_id": instance_id or "default"},
        )
        _query_logger.info(
            "query received",
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
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.info(
            "query succeeded",
            extra={
                "instance_id": context.config.instance_id,
                "row_count": len(rows),
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
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
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        _query_logger.warning(
            "query failed",
            extra={
                "instance_id": instance_id or "default",
                "error_type": exc.error_type,
                "message": exc.message,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            },
        )
        return exc.to_dict()
    except BaseException:
        _logger.exception(
            "run_query crashed",
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
            },
        )
        raise
