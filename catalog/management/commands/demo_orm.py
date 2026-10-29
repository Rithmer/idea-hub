"""Демонстрация CRUD через ORM в транзакции с обязательным откатом."""
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Idea
from participants.models import User
from taxonomy.models import Category


class Command(BaseCommand):
    """Команда демонстрации ORM без сохранения изменений."""

    help = "Демонстрация CRUD в транзакции с откатом: исходные данные не меняются."

    @transaction.atomic
    def handle(self, *args, **options):
        """Демонстрирует создание, чтение, изменение и удаление с откатом всех записей."""
        category = Category.objects.create(name="ORM demo category")
        user = User.objects.create(name="ORM demo user", password="!unusable")
        idea = Idea.objects.create(title="ORM demo idea", description="Учебная запись",
                                   category=category, author=user)
        self.stdout.write(f"CREATE: {idea.pk}; READ: {Idea.objects.get(pk=idea.pk)}")
        idea.title = "ORM demo updated"
        idea.save(update_fields=["title"])
        Idea.objects.filter(pk=idea.pk).update(status=Idea.Status.TAKEN, selected_by=user)
        idea.refresh_from_db()
        self.stdout.write(f"UPDATE: {idea.title}; выбрал: {idea.selected_by.name}")
        Idea.objects.filter(pk=idea.pk).update(status=Idea.Status.AVAILABLE, selected_by=None)
        idea.delete()
        user.delete()
        category.delete()
        self.stdout.write("DELETE: выполнено; транзакция отменена, исходные данные сохранены.")
        transaction.set_rollback(True)
