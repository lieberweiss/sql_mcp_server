from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sqlparse
from sqlparse import tokens as T
from sqlparse.sql import Identifier, IdentifierList, TokenList

from sql_mcp_server.config import DEFAULT_CONFIG, ServerConfig
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
    is_select: bool
    required_scopes: set[str]


class SQLValidator:
    def __init__(self, config: ServerConfig | None = None) -> None:
        self._config = config or DEFAULT_CONFIG

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
        is_select_like = self._is_select_like(stmt, normalized)
        required_scopes = self._required_scopes(normalized, is_select_like)

        self._check_forbidden_keywords(normalized)
        self._check_tables(stmt)

        if not is_select_like:
            if self._config.read_only:
                raise MCPError(
                    "Database is in read-only mode",
                    hint="Only SELECT queries are allowed",
                    error_type="ReadOnlyViolation",
                )
            return SQLValidationResult(
                query=normalized.rstrip().rstrip(";"),
                warnings=[],
                is_select=False,
                required_scopes=required_scopes,
            )

        rewritten, warnings = self._apply_limit(normalized)
        return SQLValidationResult(
            query=rewritten,
            warnings=warnings,
            is_select=True,
            required_scopes=required_scopes,
        )

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
        forbidden = set(FORBIDDEN_KEYWORDS)
        if self._config.allow_alter:
            forbidden.discard("ALTER")
        if self._config.allow_drop:
            forbidden.discard("DROP")
        for kw in forbidden:
            if kw in upper:
                raise MCPError(
                    f"Forbidden SQL keyword detected: {kw}",
                    hint="Remove dangerous SQL constructs",
                    error_type="ForbiddenKeyword",
                )

    def _check_tables(self, statement: TokenList) -> None:
        if not self._config.allowed_tables:
            return

        identifiers = self._extract_table_identifiers(statement)
        if not identifiers:
            return

        disallowed = identifiers - self._config.allowed_tables
        if disallowed:
            raise MCPError(
                f"Access denied to table(s): {', '.join(sorted(disallowed))}",
                hint=f"Allowed tables: {', '.join(sorted(self._config.allowed_tables))}",
                error_type="TableNotAllowed",
            )

    def _extract_table_identifiers(self, statement: TokenList) -> set[str]:
        identifiers: set[str] = set()
        for idx, token in enumerate(statement.tokens):
            if token.is_group:
                identifiers.update(self._extract_table_identifiers(token))

            if not token.ttype:
                continue

            if token.ttype not in T.Keyword:
                continue

            normalized = token.normalized.upper()
            if normalized == "FROM" or "JOIN" in normalized or normalized in {"UPDATE", "INTO", "DELETE"}:
                _, next_token = statement.token_next(idx, skip_ws=True, skip_cm=True)
                if next_token is None:
                    continue
                identifiers.update(self._identifiers_from_token(next_token))
        return identifiers

    def _identifiers_from_token(self, token) -> set[str]:
        names: set[str] = set()
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                names.update(self._identifiers_from_token(identifier))
            return names

        if isinstance(token, Identifier):
            real_name = token.get_real_name() or token.get_name()
            if real_name:
                names.add(real_name.lower())
            if token.is_group:
                names.update(self._extract_table_identifiers(token))
            return names

        if token.is_group:
            names.update(self._extract_table_identifiers(token))
            return names

        value = token.value.strip("`\" ")
        if value:
            names.add(value.lower())
        return names

    def _required_scopes(self, query: str, is_select_like: bool) -> set[str]:
        scopes: set[str] = {"r"} if is_select_like else {"w"}
        upper = query.upper()
        if self._config.allow_drop and "DROP" in upper:
            scopes.add("d")
        if self._config.allow_alter and "ALTER" in upper:
            scopes.add("a")
        return scopes

    def _apply_limit(self, query: str) -> tuple[str, list[str]]:
        normalized = query.rstrip().rstrip(";")
        q_lower = normalized.lower()
        if " limit " in q_lower or " top " in q_lower:
            return normalized, []

        if self._config.max_rows <= 0:
            return normalized, []

        if self._config.provider == "mssql":
            rewritten = normalized.replace("SELECT", f"SELECT TOP {self._config.max_rows}", 1)
            return rewritten, [f"TOP {self._config.max_rows} automatically applied"]

        limit = self._config.max_rows
        return f"{normalized} LIMIT {limit}", [f"LIMIT {limit} automatically applied"]
