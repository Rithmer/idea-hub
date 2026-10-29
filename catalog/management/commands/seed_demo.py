"""Наполнение каталога учебными данными для демонстрации пагинации."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Idea
from participants.models import User
from taxonomy.models import Category


DEMO_IDEAS = (
    ("Планировщик занятий для студентов", "Расписание занятий, дедлайны и напоминания о заданиях."),
    ("Каталог рецептов для начинающих", "Подбор рецептов по продуктам и доступному времени."),
    ("Трекер тренировок для спортсменов", "Дневник упражнений и графики изменения результатов."),
    ("Сервис заметок для исследователей", "Заметки об источниках с тегами и поиском по содержимому."),
    ("Бот напоминаний для учебной группы", "Уведомления о занятиях и совместных мероприятиях."),
    ("Учёт инвентаря для мастерской", "Каталог инструментов, мест хранения и выдачи участникам."),
    ("Планировщик поездок для туристов", "Маршруты, список вещей и бюджет путешествия."),
    ("Дневник чтения для книголюбов", "Список прочитанных книг, заметки и цели на месяц."),
    ("Мониторинг сайтов для разработчиков", "Проверка доступности сайтов и история времени ответа."),
    ("Трекер задач для команды", "Доска задач с приоритетами и сроками выполнения."),
    ("Карточки терминов для изучающих языки", "Повторение слов по интервалам и учёт прогресса."),
    ("Календарь событий для сообщества", "Поиск встреч по темам и планирование участия."),
)


class Command(BaseCommand):
    """Команда повторяемого наполнения каталога без дубликатов."""

    help = "Добавляет 12 демонстрационных идей; повторный запуск не создаёт дубликаты."

    @transaction.atomic
    def handle(self, *args, **options):
        """Добавляет отсутствующие учебные идеи, сохраняя существующие записи."""
        category = Category.objects.filter(name="Python").first()
        authors = list(User.objects.filter(is_admin=False).order_by("pk"))
        if category is None or not authors:
            raise CommandError("Сначала выполните migrate и import_pr7.")
        created = 0
        for index, (title, description) in enumerate(DEMO_IDEAS):
            if Idea.objects.filter(title=title).exists():
                continue
            idea = Idea(
                title=title, description=description, category=category,
                author=authors[index % len(authors)],
                created_at=date(2026, 10, 1) + timedelta(days=index),
            )
            idea.full_clean()
            idea.save()
            created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Добавлено идей: {created}. Всего идей: {Idea.objects.count()}."
        ))
