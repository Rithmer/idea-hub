"""Run `python -m db.import_json` to import or refresh JSON records in SQLite."""
import argparse
import sqlite3
from datetime import date
from pathlib import Path

from db.database import BASE_DIR, get_connection, initialize_database
from storage import load_categories, load_ideas, load_users


CATEGORIES_SQL = """
INSERT INTO categories (id, name) VALUES (?, ?)
ON CONFLICT(id) DO UPDATE SET name = excluded.name;
"""
USERS_SQL = """
INSERT INTO users (id, name, password, is_admin) VALUES (?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET name = excluded.name,
    password = excluded.password, is_admin = excluded.is_admin;
"""
IDEAS_SQL = """
INSERT INTO ideas (id, title, description, category_id, author_id, status,
                   selected_by_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET title = excluded.title,
    description = excluded.description, category_id = excluded.category_id,
    author_id = excluded.author_id, status = excluded.status,
    selected_by_id = excluded.selected_by_id, created_at = excluded.created_at;
"""


def import_json(data_dir: Path | None = None, db_path: Path | None = None) -> dict[str, int]:
    directory = data_dir if data_dir is not None else BASE_DIR / "data"
    # Missing input is an import error, rather than an empty source dataset.
    for filename in ("categories.json", "users.json", "ideas.json"):
        if not (directory / filename).is_file():
            raise ValueError(f"Не найден исходный файл {filename}")
    categories = load_categories(directory / "categories.json")
    users = load_users(directory / "users.json")
    ideas = load_ideas(directory / "ideas.json")
    for idea in ideas:
        if date.fromisoformat(idea.created_at).isoformat() != idea.created_at:
            raise ValueError("Дата создания должна иметь формат YYYY-MM-DD")
    for entities in (categories, users, ideas):
        ids = [entity.id for entity in entities]
        if len(ids) != len(set(ids)):
            raise ValueError("В исходных данных повторяются идентификаторы")
    initialize_database(db_path)
    conn = get_connection(db_path)
    try:
        conn.execute("BEGIN")
        conn.executemany(CATEGORIES_SQL, [(item.id, item.name) for item in categories])
        conn.executemany(USERS_SQL, [
            (item.id, item.name, item.password, int(item.is_admin)) for item in users
        ])
        conn.executemany(IDEAS_SQL, [
            (item.id, item.title, item.description, item.category_id, item.author_id,
             item.status.value, item.selected_by_id, item.created_at) for item in ideas
        ])
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        raise
    finally:
        conn.close()
    return {"categories": len(categories), "users": len(users), "ideas": len(ideas)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Перенос данных IdeaHub из JSON в SQLite")
    parser.add_argument("--data-dir", type=Path, help="Каталог исходных JSON-файлов")
    parser.add_argument("--database", type=Path, help="Файл базы SQLite")
    args = parser.parse_args()
    try:
        counts = import_json(args.data_dir, args.database)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Импорт не выполнен: {error}\n")
    print("Импорт завершён: " + ", ".join(f"{name}: {count}" for name, count in counts.items()))


if __name__ == "__main__":
    main()
