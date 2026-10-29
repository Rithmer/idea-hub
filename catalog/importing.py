"""Чтение снимка ПР7 и проверяемый атомарный перенос в модели Django."""
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import models, transaction

from catalog.models import Idea
from participants.models import User
from taxonomy.models import Category


@dataclass(frozen=True)
class Pr7Snapshot:
    """Поля исходных записей с датами и логическими значениями в типах Python."""

    categories: list[dict[str, Any]]
    users: list[dict[str, Any]]
    ideas: list[dict[str, Any]]


def _read_pr7(source: Path) -> Pr7Snapshot:
    """Читает согласованный снимок исходной базы без возможности записи в неё."""
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Исходная база повреждена.")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("В исходной базе нарушены внешние ключи.")
        categories = [dict(row) for row in connection.execute("SELECT id, name FROM categories")]
        users = [dict(row) for row in connection.execute("SELECT id, name, password, is_admin FROM users")]
        ideas = [dict(row) for row in connection.execute(
            "SELECT id, title, description, category_id, author_id, status, "
            "selected_by_id, created_at FROM ideas"
        )]
    for row in users:
        if row["is_admin"] not in (0, 1):
            raise ValueError("Некорректный признак администратора.")
        row["is_admin"] = bool(row["is_admin"])
    for row in ideas:
        row["created_at"] = date.fromisoformat(row["created_at"])
    return Pr7Snapshot(categories=categories, users=users, ideas=ideas)


def _save_and_verify(model: type[models.Model], rows: list[dict[str, Any]]) -> None:
    """Проверяет модели до вставки и сравнивает все сохранённые поля с источником."""
    for row in rows:
        obj = model(**row)
        obj.full_clean()
        obj.save(force_insert=True)
    actual = list(model._default_manager.order_by("id").values(*rows[0])) if rows else []
    if actual != sorted(rows, key=lambda row: row["id"]):
        raise ValueError(f"Проверка переноса {model.__name__} не пройдена.")


def import_pr7(source: Path) -> Pr7Snapshot:
    """Переносит данные в пустую базу; любая ошибка откатывает все вставки."""
    source = source.resolve()
    if not source.is_file():
        raise ValueError(f"Исходная база не найдена: {source}")
    target = Path(settings.DATABASES["default"]["NAME"]).resolve()
    if source == target:
        raise ValueError("Исходная и целевая базы должны быть разными файлами.")
    snapshot = _read_pr7(source)
    with transaction.atomic():
        if Category.objects.exists() or User.objects.exists() or Idea.objects.exists():
            raise ValueError("Целевые таблицы не пусты; повторный перенос запрещён.")
        for model, rows in ((Category, snapshot.categories), (User, snapshot.users),
                            (Idea, snapshot.ideas)):
            _save_and_verify(model, rows)
    return snapshot
