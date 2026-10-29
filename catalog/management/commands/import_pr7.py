"""Перенос данных из базы ПР7 в Django через ORM без изменения источника."""
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from catalog.importing import import_pr7


class Command(BaseCommand):
    """Команда проверяемого переноса данных ПР7 с сохранением идентификаторов и связей."""

    help = "Перенос данных ПР7 в пустые таблицы Django с сохранением ID и связей."

    def add_arguments(self, parser):
        """Добавляет параметр пути к исходной базе ПР7."""
        parser.add_argument("--source", type=Path,
                            default=settings.BASE_DIR / "data" / "idea_hub.sqlite")

    def handle(self, *args, **options):
        """Читает источник без записи и атомарно переносит данные в пустые таблицы Django."""
        try:
            snapshot = import_pr7(Path(options["source"]))
        except (sqlite3.Error, IntegrityError, ValidationError, ValueError, TypeError) as error:
            raise CommandError(f"Перенос отменён, данные не записаны: {error}") from error
        self.stdout.write(self.style.SUCCESS(
            f"Перенос завершён: categories: {len(snapshot.categories)}, "
            f"users: {len(snapshot.users)}, ideas: {len(snapshot.ideas)}"
        ))
