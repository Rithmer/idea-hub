import json
import shutil
import sqlite3
from contextlib import closing

import pytest

from db import database
from db.import_json import import_json
from db.queries import fetch_all, fetch_ideas, fetch_one
from models import Status


def source_copy(tmp_path):
    directory = tmp_path / "source"
    directory.mkdir()
    for name in ("categories", "users", "ideas"):
        shutil.copy2(database.BASE_DIR / "data" / f"{name}.json", directory)
    return directory


def test_connection_schema_and_integrity(sqlite_database, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with closing(database.get_connection()) as conn:
        assert conn.row_factory is sqlite3.Row
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not conn.execute("PRAGMA foreign_key_check").fetchall()
        assert {row["table"] for row in conn.execute("PRAGMA foreign_key_list(ideas)")} == {
            "categories", "users",
        }
        assert {row["name"] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )} == {"ideas", "categories", "users"}
    assert fetch_one("idea_totals")["total"] == 4


def test_import_preserves_relations_and_repeated_import_has_no_duplicates(sqlite_database):
    assert import_json() == {"categories": 5, "users": 5, "ideas": 4}
    assert import_json() == {"categories": 5, "users": 5, "ideas": 4}
    idea = fetch_one("idea_detail", (2,))
    assert idea["category_name"] == "JavaScript"
    assert idea["author_name"] == idea["selected_by_name"] == "Иван Петров"
    assert idea["status"] == Status.TAKEN
    assert fetch_one("idea_totals")["total"] == 4
    assert len(fetch_all("users")) == len(fetch_all("categories")) == 5


@pytest.mark.parametrize("statement, parameters", [
    ("UPDATE ideas SET category_id = ? WHERE id = 1", (999,)),
    ("UPDATE ideas SET author_id = ? WHERE id = 1", (999,)),
    ("UPDATE ideas SET status = ? WHERE id = 1", ("invalid",)),
    ("UPDATE ideas SET status = ? WHERE id = 1", ("взята",)),
    ("UPDATE ideas SET selected_by_id = ? WHERE id = 2", (None,)),
    ("UPDATE ideas SET status = ?, selected_by_id = ? WHERE id = 1", ("взята", 3)),
    ("UPDATE users SET is_admin = ? WHERE id = 1", (2,)),
    ("DELETE FROM categories WHERE id = 1", ()),
])
def test_invalid_relations_and_states_are_rejected(statement, parameters):
    with closing(database.get_connection()) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(statement, parameters)
        conn.rollback()
    assert fetch_one("idea_totals")["available"] == 3


def test_failed_import_rolls_back_all_tables(tmp_path):
    directory = source_copy(tmp_path)
    categories_path = directory / "categories.json"
    categories = json.loads(categories_path.read_text())
    categories[0]["name"] = "Changed category"
    categories_path.write_text(json.dumps(categories))
    ideas_path = directory / "ideas.json"
    ideas = json.loads(ideas_path.read_text())
    ideas[0]["title"] = "Changed title"
    ideas[-1]["category_id"] = 999
    ideas_path.write_text(json.dumps(ideas))
    with pytest.raises(sqlite3.IntegrityError):
        import_json(directory)
    assert fetch_one("category_detail", (1,))["name"] == "Python"
    assert fetch_one("idea_detail", (1,))["title"] != "Changed title"
    assert fetch_one("idea_totals")["total"] == 4


@pytest.mark.parametrize("problem", ["missing", "malformed", "duplicate", "date"])
def test_import_rejects_invalid_source_without_altering_data(tmp_path, problem):
    directory = source_copy(tmp_path)
    path = directory / "ideas.json"
    ideas = json.loads(path.read_text())
    if problem == "missing":
        path.unlink()
    elif problem == "malformed":
        path.write_text("{")
    elif problem == "duplicate":
        path.write_text(json.dumps(ideas + ideas[:1]))
    else:
        ideas[0]["created_at"] = "2026-02-30"
        path.write_text(json.dumps(ideas))
    with pytest.raises(ValueError):
        import_json(directory)
    assert fetch_one("idea_totals")["total"] == 4


def test_filtering_joins_aggregation_and_having():
    assert [row["id"] for row in fetch_ideas("available_ideas", ("", "", 1, 1))] == [1, 4]
    assert [row["id"] for row in fetch_ideas("selected_ideas")] == [2]
    assert [row["id"] for row in fetch_ideas("category_ideas", (3,))] == [2]
    assert dict(fetch_one("idea_totals")) == {
        "total": 4, "available": 3, "taken": 1,
        "first_created": "2026-08-28", "last_created": "2026-09-09",
    }
    assert dict(fetch_one("user_totals")) == {"authors": 4, "selectors": 1}
    categories = {row["name"]: row["count"] for row in fetch_all("category_statistics")}
    assert categories == {"Python": 2, "Java": 1, "JavaScript": 1, "C#": 0, "Go": 0}
    assert len(fetch_all("author_statistics")) == 5
    assert [row["name"] for row in fetch_all("popular_categories", (2,))] == ["Python"]
    assert fetch_all("popular_categories", (3,)) == []
    assert len(fetch_all("popular_categories", (0,))) == 5
    assert {row["status"]: row["count"] for row in fetch_all("status_statistics")} == {
        "не взята": 3, "взята": 1,
    }


def test_query_connections_are_read_only():
    with closing(database.get_connection(read_only=True)) as conn:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("DELETE FROM ideas")
