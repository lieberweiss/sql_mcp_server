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
- Automatic row limiting (`LIMIT` / `TOP`)
- Optional table allowlist (`DB_ALLOWED_TABLES`)
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
- `DB_ALLOWED_TABLES` (optional, comma-separated allowlist)

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
        "DB_QUERY_TIMEOUT": "10",
        "DB_ALLOWED_TABLES": ""
      }
    }
  }
}
```

## MCP tools

- `list_tables`: List accessible tables
- `describe_table(table: str)`: Describe columns of a table
- `run_select(query: str)`: Execute a validated, safe SELECT query

## Security notes

- Always use a database user with the least privileges possible.
- Prefer DB-level read-only privileges in addition to middleware enforcement.

## License

MIT
