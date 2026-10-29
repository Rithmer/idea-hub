"""Загрузка и выполнение именованных SQL-запросов слоя ПР7."""
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from db.database import BASE_DIR, get_connection


QUERY_PATH = BASE_DIR / "sql" / "queries.sql"


def load_queries(path: Path = QUERY_PATH) -> dict[str, str]:
    """Читает запросы с заголовками -- name: из одного SQL-файла."""
    queries: dict[str, str] = {}
    name = None
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("-- name: "):
            if name is not None:
                raise ValueError("Незавершённое SQL-выражение.")
            name = line.removeprefix("-- name: ").strip()
            if not name.isidentifier() or name in queries:
                raise ValueError("Имя SQL-запроса должно быть допустимым и уникальным.")
        elif name is not None:
            lines.append(line)
            if sqlite3.complete_statement("".join(lines)):
                queries[name] = "".join(lines).strip()
                name = None
                lines = []
        elif line.strip() and not line.lstrip().startswith("--"):
            raise ValueError("Перед SQL-запросом требуется заголовок -- name: имя.")
    if name is not None:
        raise ValueError("Незавершённое SQL-выражение.")
    return queries


QUERIES = load_queries()
SqlValue = str | int | None


def fetch_all(name: str, parameters: tuple[SqlValue, ...] = ()) -> list[sqlite3.Row]:
    """Выполняет именованный запрос в режиме чтения и возвращает все строки."""
    with closing(get_connection(read_only=True)) as conn:
        return conn.execute(QUERIES[name], parameters).fetchall()


def fetch_one(name: str, parameters: tuple[SqlValue, ...] = ()) -> sqlite3.Row | None:
    """Выполняет именованный запрос в режиме чтения и возвращает одну строку или None."""
    with closing(get_connection(read_only=True)) as conn:
        return conn.execute(QUERIES[name], parameters).fetchone()


def present_idea(row: sqlite3.Row) -> dict[str, Any]:
    """Преобразует строку SQL в словарь с вложенными связанными объектами для шаблонов."""
    idea = dict(row)
    idea["category"] = {"id": row["category_id"], "name": row["category_name"]}
    idea["author"] = {"id": row["author_id"], "name": row["author_name"]}
    idea["selected_by"] = (
        {"id": row["selected_by_id"], "name": row["selected_by_name"]}
        if row["selected_by_id"] is not None else None
    )
    return idea


def fetch_ideas(name: str, parameters: tuple[SqlValue, ...] = ()) -> list[dict[str, Any]]:
    """Выполняет запрос и готовит вложенные словари идей для отображения."""
    return [present_idea(row) for row in fetch_all(name, parameters)]
