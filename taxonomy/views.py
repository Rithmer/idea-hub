"""Список категорий со счётчиками и подробная страница категории."""
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from catalog.queries import category_statistics
from taxonomy.models import Category


def categories(request: HttpRequest) -> HttpResponse:
    """Показывает категории с числом идей, включая пустые категории."""
    category_cards = [
        {"category": row, "count": row.count}
        for row in category_statistics()
    ]
    return render(request, "taxonomy/category_list.html",
                  {"category_cards": category_cards})


def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    """Показывает категорию и связанные идеи или возвращает страницу 404."""
    try:
        category = get_object_or_404(Category, pk=category_id)
    except Http404:
        return render(request, "taxonomy/category_not_found.html", status=404)
    context = {
        "category": category,
        "ideas": category.ideas.select_related("category", "author", "selected_by"),
    }
    return render(request, "taxonomy/category_detail.html", context)
