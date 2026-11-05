"""ORM-запросы каталога: поиск, связанные объекты и статистика."""
from datetime import date
from typing import TypedDict

from django.db.models import Count, F, Max, Min, Q, QuerySet
from django_stubs_ext import WithAnnotations

from catalog.models import Idea, IdeaQuerySet
from participants.models import User
from taxonomy.models import Category


SORT_ORDERS = {
    "newest": ("-created_at", "-pk"),
    "oldest": ("created_at", "pk"),
    "title": ("title", "pk"),
    "category": ("category__name", "title", "pk"),
}


def idea_listing() -> IdeaQuerySet:
    """Возвращает идеи с заранее загруженными категорией, автором и участником."""
    return Idea.objects.with_people_and_category()


def filtered_ideas(q: str = "", category: int | None = None,
                   author: int | None = None, status: str = "", *,
                   extended: bool = False, created_at: date | None = None) -> IdeaQuerySet:
    """Фильтрует идеи; расширенный поиск учитывает описание и название категории."""
    listing = idea_listing()
    if q:
        condition = Q(title__icontains=q)
        if extended:
            condition |= Q(description__icontains=q) | Q(category__name__icontains=q)
        listing = listing.filter(condition)
    if category is not None:
        listing = listing.filter(category_id=category)
    if author is not None:
        listing = listing.filter(author_id=author)
    if status:
        listing = listing.filter(status=status)
    if created_at is not None:
        listing = listing.filter(created_at=created_at)
    return listing


def available_ideas(q: str = "", category: int | None = None) -> QuerySet[Idea]:
    """Ищет свободные идеи, исключая уже выбранные участниками."""
    return filtered_ideas(q, category, extended=True).available()


def selected_ideas():
    """Возвращает только поля страницы выбранных идей, включая имена из связанных таблиц."""
    return (
        Idea.objects.taken()
        .annotate(
            category_name=F("category__name"),
            author_name=F("author__name"),
            selected_by_name=F("selected_by__name"),
            # Словари сохраняют интерфейс общего шаблона статуса идеи.
            is_available=Q(status=Idea.Status.AVAILABLE),
        )
        .values("id", "title", "category_name", "author_name", "selected_by_name", "is_available")
    )


def idea_totals():
    """Подсчитывает идеи по статусам и определяет диапазон дат создания."""
    return Idea.objects.aggregate(
        total=Count("pk"),
        available=Count("pk", filter=Q(status=Idea.Status.AVAILABLE)),
        taken=Count("pk", filter=Q(status=Idea.Status.TAKEN)),
        first_created=Min("created_at"), last_created=Max("created_at"),
    )


def user_totals():
    """Подсчитывает уникальных авторов и участников, выбравших идеи."""
    return Idea.objects.aggregate(
        authors=Count("author", distinct=True),
        selectors=Count("selected_by", distinct=True),
    )


class CategoryCounts(TypedDict):
    count: int
    available: int
    taken: int


def category_statistics() -> QuerySet[WithAnnotations[Category, CategoryCounts]]:
    """Подсчитывает идеи по категориям, включая категории без идей."""
    return Category.objects.annotate(
        count=Count("ideas"),
        available=Count("ideas", filter=Q(ideas__status=Idea.Status.AVAILABLE)),
        taken=Count("ideas", filter=Q(ideas__status=Idea.Status.TAKEN)),
    ).order_by("name", "pk")


def author_statistics() -> QuerySet[User]:
    """Подсчитывает все и свободные идеи каждого участника, включая нулевые."""
    return User.objects.annotate(
        count=Count("authored_ideas"),
        available=Count("authored_ideas", filter=Q(authored_ideas__status=Idea.Status.AVAILABLE)),
    ).order_by("-count", "name", "pk")


def popular_categories(minimum: int) -> QuerySet[WithAnnotations[Category, CategoryCounts]]:
    """Отбирает категории с числом идей не меньше заданного порога."""
    return category_statistics().filter(count__gte=minimum).order_by("-count", "name", "pk")


def status_statistics():
    """Группирует идеи по статусу и подсчитывает размер каждой группы."""
    return Idea.objects.values("status").annotate(count=Count("pk")).order_by("status")
