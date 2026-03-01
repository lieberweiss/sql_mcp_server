# sql-mcp-server

A secure Model Context Protocol (MCP) server that exposes database access to LLM clients via **FastMCP**.

Supported database providers:

- SQLite
- PostgreSQL
- MySQL
- Microsoft SQL Server (MSSQL)

## Features

- Safe-by-default SQL validation middleware
- Read-only mode (`DB_READ_ONLY=true`) enforced before execution
- Single statement enforcement
- Forbidden keyword detection
- Granular opt-in for destructive statements (e.g. allow `DROP` via `DB_ALLOW_DROP=true`)
- Automatic row limiting (`LIMIT` / `TOP`)
- Optional table allowlist (`DB_ALLOWED_TABLES`)
- Multi-instance runtime: expose several databases from a single MCP server
- MCP tools designed for schema exploration and safe querying

## Project structure

```text
src/sql_mcp_server/
  main.py
  config.py
  errors.py
  middleware/sql_validator.py
  db/
  tools/
```

## Configuration

Copy `.env.example` to `.env` and update values.

### Multi-instance setup

Set `MCP_INSTANCES` to a comma-separated list of prefixes (e.g. `MCP_INSTANCES=CRM,ERP`).
For every prefix, define the expected environment variables by upper-casing the prefix and
suffixing standard keys: `CRM_DB_PROVIDER`, `CRM_DB_HOST`, etc. Instance identifiers are
case-insensitive and available to tools via the `instance_id` parameter.

When `MCP_INSTANCES` is omitted, the server exposes a single `default` instance sourced
directly from the un-prefixed environment variables shown below.

### SQLite

```env
DB_PROVIDER=sqlite
SQLITE_PATH=./database.db
DB_READ_ONLY=true
DB_MAX_ROWS=100
```

### PostgreSQL

```env
DB_PROVIDER=postgres
DB_HOST=localhost
DB_PORT=5432
DB_USER=myuser
DB_PASSWORD=mypassword
DB_DATABASE=mydb
DB_READ_ONLY=true
DB_MAX_ROWS=100
```

### MySQL

```env
DB_PROVIDER=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=mypassword
DB_DATABASE=mydb
DB_READ_ONLY=true
DB_MAX_ROWS=100
```

### MSSQL

```env
DB_PROVIDER=mssql
DB_HOST=localhost
DB_PORT=1433
DB_USER=myuser
DB_PASSWORD=mypassword
DB_DATABASE=mydb
DB_READ_ONLY=true
DB_MAX_ROWS=100
```

> ℹ️ The MSSQL client applies `DB_QUERY_TIMEOUT` via the pyodbc connection timeout when provided; ensure the driver you select supports this property.
> ⚠️ Make sure to install a SQL Server ODBC driver (e.g., `msodbcsql17` / `msodbcsql18`) before starting the MSSQL instance, otherwise `pyodbc` cannot establish the connection.

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .
```

## Run

```bash
sql-mcp-server
```

The server runs over stdio (FastMCP default) and can be wired to MCP-compatible clients.

## Windsurf configuration (mcp_config.json)

Windsurf can launch this MCP server over stdio. You can configure it in:

`~/.codeium/windsurf/mcp_config.json`

The examples below use the "module" entrypoint (Option 2):

- `command`: your venv Python executable
- `args`: `["-m", "sql_mcp_server.main"]`

### Common optional env fields

- `DB_READ_ONLY` (optional, default: `true`)
- `DB_MAX_ROWS` (optional, default: `100`)
- `DB_QUERY_TIMEOUT` (optional, default: `10` seconds)
- `DB_STATEMENT_TIMEOUT_MS` (optional, default: `DB_QUERY_TIMEOUT * 1000`; caps statement execution time)
- `DB_ALLOWED_TABLES` (optional, comma-separated allowlist)
- `DB_ALLOW_ALTER` (optional, default: `false`; when `true`, the validator lets `ALTER` statements pass so you can evolve schemas without fully disabling keyword protection)
- `DB_ALLOW_DROP` (optional, default: `false`; set to `true` only when you intentionally need to run `DROP` statements)
- `ENABLE_QUERY_LOGS` (optional, default: `false`; when enabled, SQL metadata is logged to `logs/queries.log` with daily rotation)
- `LOG_QUERY_BODIES` (optional, default: `false`; when `true`, full SQL text is logged in addition to the hashed metadata—keep disabled in production)
- `SQL_MCP_LOG_LEVEL` (optional, default: `INFO`; override to reduce verbosity in production, e.g. `WARNING`)

### SQLite (Windsurf)

Required env fields:

- `DB_PROVIDER=sqlite`
- `SQLITE_PATH`

```json
{
  "mcpServers": {
    "sql-sqlite": {
      "command": "c:\\dev\\code\\mcp\\sql_mcp_server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "sql_mcp_server.main"],
      "disabled": false,
      "env": {
        "DB_PROVIDER": "sqlite",
        "SQLITE_PATH": "./database.db",
        "DB_READ_ONLY": "true",
        "DB_MAX_ROWS": "100",
        "DB_QUERY_TIMEOUT": "10",
        "DB_ALLOWED_TABLES": ""
      }
    }
  }
}
```

### PostgreSQL (Windsurf)

Required env fields:

- `DB_PROVIDER=postgres`
- `DB_HOST`
- `DB_PORT` (optional, default driver-side; recommended to set)
- `DB_USER`
- `DB_PASSWORD`
- `DB_DATABASE`

```json
{
  "mcpServers": {
    "sql-postgres": {
      "command": "c:\\dev\\code\\mcp\\sql_mcp_server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "sql_mcp_server.main"],
      "disabled": false,
      "env": {
        "DB_PROVIDER": "postgres",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_USER": "myuser",
        "DB_PASSWORD": "mypassword",
        "DB_DATABASE": "mydb",
        "DB_READ_ONLY": "true",
        "DB_MAX_ROWS": "100",
        "DB_QUERY_TIMEOUT": "10",
        "DB_ALLOWED_TABLES": ""
      }
    }
  }
}
```

### MySQL (Windsurf)

Required env fields:

- `DB_PROVIDER=mysql`
- `DB_HOST`
- `DB_PORT` (optional, default driver-side; recommended to set)
- `DB_USER`
- `DB_PASSWORD`
- `DB_DATABASE`

```json
{
  "mcpServers": {
    "sql-mysql": {
      "command": "c:\\dev\\code\\mcp\\sql_mcp_server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "sql_mcp_server.main"],
      "disabled": false,
      "env": {
        "DB_PROVIDER": "mysql",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "myuser",
        "DB_PASSWORD": "mypassword",
        "DB_DATABASE": "mydb",
        "DB_READ_ONLY": "true",
        "DB_MAX_ROWS": "100",
        "DB_QUERY_TIMEOUT": "10",
        "DB_ALLOWED_TABLES": ""
      }
    }
  }
}
```

### MSSQL (Windsurf)

Required env fields:

- `DB_PROVIDER=mssql`
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_DATABASE`

Optional env fields:

- `DB_PORT` (optional; default: `1433`)
- `DB_MSSQL_ODBC_DRIVER` (optional; if unset the server will try: `ODBC Driver 18 for SQL Server`, then `ODBC Driver 17 for SQL Server`, then `SQL Server`)
- `DB_MSSQL_TRUST_SERVER_CERTIFICATE` (optional; default: `false`; set to `true` for local/dev when using a self-signed certificate)

```json
{
  "mcpServers": {
    "sql-mssql": {
      "command": "c:\\dev\\code\\mcp\\sql_mcp_server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "sql_mcp_server.main"],
      "disabled": false,
      "env": {
        "DB_PROVIDER": "mssql",
        "DB_HOST": "localhost",
        "DB_PORT": "1433",
        "DB_USER": "myuser",
        "DB_PASSWORD": "mypassword",
        "DB_DATABASE": "mydb",
        "DB_MSSQL_ODBC_DRIVER": "ODBC Driver 17 for SQL Server",
        "DB_MSSQL_TRUST_SERVER_CERTIFICATE": "true",
        "DB_READ_ONLY": "true",
        "DB_MAX_ROWS": "100",
        "DB_ALLOWED_TABLES": ""
      }
    }
  }
}
```

## MCP tools

- `list_tables(instance_id?: str)`: List accessible tables for the selected instance
- `describe_table(table: str, instance_id?: str)`: Columns for a specific table
- `run_select(query: str, instance_id?: str)`: Execute a validated, safe SELECT query
- `run_query(query: str, instance_id?: str)`: Execute a validated query (write statements allowed when the instance is not read-only)

When embedding the server, call `sql_mcp_server.instances.shutdown_instance_registry()` during teardown to close database connections cleanly.

### Logging & privacy

- Log files live in `logs/` and are rotated daily; they are created with `0600` permissions to avoid accidental exposure.
- Query logs store only query length and a SHA-256 hash by défaut; enable them via `ENABLE_QUERY_LOGS=true`, puis activez `LOG_QUERY_BODIES=true` uniquement si nécessaire pour le débogage.
- Ajustez `SQL_MCP_LOG_LEVEL` pour limiter la verbosité en production.

## Security notes

- Always use a database user with the least privileges possible.
- Prefer DB-level read-only privileges in addition to middleware enforcement.

## License

MIT
