"""Изолированная база и исходные данные для проверок веб-приложения."""
import os

import django
import pytest
from django.test import Client
from django.test.utils import (
    setup_databases, setup_test_environment, teardown_databases, teardown_test_environment,
)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_hub.settings")
django.setup()


@pytest.fixture(scope="session")
def django_database():
    """Создаёт отдельную тестовую базу с миграциями проекта."""
    setup_test_environment()
    configuration = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(configuration, verbosity=0)
    teardown_test_environment()


@pytest.fixture(autouse=True)
def catalog_data(django_database):
    """Наполняет тестовый каталог; изменения каждого теста откатываются."""
    from django.db import transaction

    from catalog.models import Idea
    from participants.models import User
    from taxonomy.models import Category

    with transaction.atomic():
        Category.objects.bulk_create([
            Category(id=1, name="Python"), Category(id=2, name="Java"),
            Category(id=3, name="JavaScript"), Category(id=4, name="C#"),
            Category(id=5, name="Go"),
        ])
        User.objects.bulk_create([
            User(id=1, name="Администратор", password="!", is_admin=True),
            User(id=2, name="Анна Смирнова", password="!"),
            User(id=3, name="Иван Петров", password="!"),
            User(id=4, name="Мария Кузнецова", password="!"),
            User(id=5, name="Дмитрий Соколов", password="!"),
        ])
        Idea.objects.bulk_create([
            Idea(id=1, title="Приложение для поиска волонтёрских проектов",
                 description="Сервис для поиска инициатив рядом с пользователем.",
                 category_id=1, author_id=2, created_at="2026-09-09"),
            Idea(id=2, title="Трекер привычек с геймификацией",
                 description="Приложение для отслеживания привычек с очками.",
                 category_id=3, author_id=3, status=Idea.Status.TAKEN,
                 selected_by_id=3, created_at="2026-09-05"),
            Idea(id=3, title="Платформа для обмена книгами",
                 description="Сервис для бесплатного обмена книгами между соседями.",
                 category_id=2, author_id=4, created_at="2026-08-28"),
            Idea(id=4, title="Трекер расходов для студентов",
                 description="Приложение для учёта расходов и планирования стипендии.",
                 category_id=1, author_id=5, created_at="2026-09-01"),
        ])
        yield
        transaction.set_rollback(True)


@pytest.fixture
def client():
    """HTTP-клиент Django для запросов к страницам сайта."""
    return Client()
