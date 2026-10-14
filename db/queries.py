"""Execute the named statements in sql/queries.sql without duplicating SQL in views."""
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from db.database import BASE_DIR, get_connection


QUERY_PATH = BASE_DIR / "sql" / "queries.sql"


def load_queries(path: Path = QUERY_PATH) -> dict[str, str]:
    queries: dict[str, str] = {}
    name = ""
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name: "):
            if name:
                queries[name] = "\n".join(lines).strip()
            name = line.removeprefix("-- name: ").strip()
            lines = []
        elif name:
            lines.append(line)
    if name:
        queries[name] = "\n".join(lines).strip()
    return queries


QUERIES = load_queries()
SqlValue = str | int | None


def fetch_all(name: str, parameters: tuple[SqlValue, ...] = ()) -> list[sqlite3.Row]:
    with closing(get_connection(read_only=True)) as conn:
        return conn.execute(QUERIES[name], parameters).fetchall()


def fetch_one(name: str, parameters: tuple[SqlValue, ...] = ()) -> sqlite3.Row | None:
    with closing(get_connection(read_only=True)) as conn:
        return conn.execute(QUERIES[name], parameters).fetchone()


def present_idea(row: sqlite3.Row) -> dict[str, Any]:
    """Preserve the nested context structure used by the PR6 card templates."""
    idea = dict(row)
    idea["category"] = {"id": row["category_id"], "name": row["category_name"]}
    idea["author"] = {"id": row["author_id"], "name": row["author_name"]}
    idea["selected_by"] = (
        {"id": row["selected_by_id"], "name": row["selected_by_name"]}
        if row["selected_by_id"] is not None else None
    )
    return idea


def fetch_ideas(name: str, parameters: tuple[SqlValue, ...] = ()) -> list[dict[str, Any]]:
    return [present_idea(row) for row in fetch_all(name, parameters)]
