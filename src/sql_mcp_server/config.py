import os

DB_PROVIDER = os.getenv("DB_PROVIDER", "sqlite").lower()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else None
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

SQLITE_PATH = os.getenv("SQLITE_PATH", "./database.db")

DB_READ_ONLY = os.getenv("DB_READ_ONLY", "true").lower() == "true"
DB_MAX_ROWS = int(os.getenv("DB_MAX_ROWS", "100"))
DB_QUERY_TIMEOUT = int(os.getenv("DB_QUERY_TIMEOUT", "10"))
DB_STATEMENT_TIMEOUT_MS = int(
    os.getenv("DB_STATEMENT_TIMEOUT_MS", str(DB_QUERY_TIMEOUT * 1000))
)
DB_STATEMENT_TIMEOUT_SECONDS = max((DB_STATEMENT_TIMEOUT_MS + 999) // 1000, 1)

DB_ALLOWED_TABLES = {
    t.strip().lower()
    for t in os.getenv("DB_ALLOWED_TABLES", "").split(",")
    if t.strip()
}
