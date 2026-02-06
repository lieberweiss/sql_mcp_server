from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sqlparse

from sql_mcp_server.config import DB_ALLOWED_TABLES, DB_MAX_ROWS, DB_PROVIDER, DB_READ_ONLY
from sql_mcp_server.errors import MCPError

FORBIDDEN_KEYWORDS = {
    "DROP",
    "ALTER",
    "TRUNCATE",
    "EXEC",
    "MERGE",
    "GRANT",
    "REVOKE",
    "DENY",
    "CALL",
    "XP_",
    "SP_",
}


@dataclass(frozen=True)
class SQLValidationResult:
    query: str
    warnings: list[str]


class SQLValidator:
    def validate(self, query: str) -> SQLValidationResult:
        normalized = query.strip()
        if not normalized:
            raise MCPError("Query is empty", error_type="InvalidQuery")

        statements = sqlparse.parse(normalized)
        if len(statements) != 1:
            raise MCPError(
                "Only one SQL statement is allowed",
                hint="Send a single SELECT statement",
                error_type="MultipleStatementsNotAllowed",
            )

        stmt = statements[0]
        if not self._is_select_like(stmt, normalized):
            if DB_READ_ONLY:
                raise MCPError(
                    "Database is in read-only mode",
                    hint="Only SELECT queries are allowed",
                    error_type="ReadOnlyViolation",
                )
            raise MCPError(
                "Only SELECT queries are allowed",
                hint="Use the run_select tool",
                error_type="NonSelectNotAllowed",
            )

        self._check_forbidden_keywords(normalized)
        self._check_tables(normalized)

        rewritten, warnings = self._apply_limit(normalized)
        return SQLValidationResult(query=rewritten, warnings=warnings)

    def _is_select_like(self, stmt, raw: str) -> bool:
        stmt_type = (stmt.get_type() or "").upper()
        if stmt_type == "SELECT":
            return True

        raw_upper = raw.lstrip().upper()
        if raw_upper.startswith("WITH "):
            return " SELECT " in raw_upper or raw_upper.startswith("WITH")

        return False

    def _check_forbidden_keywords(self, query: str) -> None:
        upper = query.upper()
        for kw in FORBIDDEN_KEYWORDS:
            if kw in upper:
                raise MCPError(
                    f"Forbidden SQL keyword detected: {kw}",
                    hint="Remove dangerous SQL constructs",
                    error_type="ForbiddenKeyword",
                )

    def _check_tables(self, query: str) -> None:
        if not DB_ALLOWED_TABLES:
            return

        parsed = sqlparse.parse(query)
        if not parsed:
            return

        identifiers = {
            token.value.lower()
            for token in parsed[0].tokens
            if token.ttype is None and token.value.isidentifier()
        }

        if not identifiers:
            return

        disallowed = identifiers - DB_ALLOWED_TABLES
        if disallowed:
            raise MCPError(
                f"Access denied to table(s): {', '.join(sorted(disallowed))}",
                hint=f"Allowed tables: {', '.join(sorted(DB_ALLOWED_TABLES))}",
                error_type="TableNotAllowed",
            )

    def _apply_limit(self, query: str) -> tuple[str, list[str]]:
        normalized = query.rstrip().rstrip(";")
        q_lower = normalized.lower()
        if " limit " in q_lower or " top " in q_lower:
            return normalized, []

        if DB_MAX_ROWS <= 0:
            return normalized, []

        if DB_PROVIDER == "mssql":
            rewritten = normalized.replace("SELECT", f"SELECT TOP {DB_MAX_ROWS}", 1)
            return rewritten, [f"TOP {DB_MAX_ROWS} automatically applied"]

        return f"{normalized} LIMIT {DB_MAX_ROWS}", [f"LIMIT {DB_MAX_ROWS} automatically applied"]
