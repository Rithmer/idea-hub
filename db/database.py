"""Connections and schema creation independent of Django ORM."""
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "idea_hub.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(db_path: Path | None = None, *, read_only: bool = False) -> sqlite3.Connection:
    path = (db_path if db_path is not None else DB_PATH).resolve()
    if read_only:
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(db_path: Path | None = None) -> None:
    path = db_path if db_path is not None else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Схема SQLite создана.")
