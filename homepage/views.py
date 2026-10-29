"""Главная страница каталога и общий обработчик ошибки 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from catalog.queries import idea_listing, idea_totals
from taxonomy.models import Category


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Возвращает общую страницу 404 без внутренних подробностей ошибки."""
    return render(request, "404.html", status=404)


def index(request: HttpRequest) -> HttpResponse:
    """Показывает три последние идеи, категории и сводные счётчики."""
    totals = idea_totals()
    context = {
        "ideas": idea_listing().order_by("-created_at", "-pk")[:3],
        "categories": Category.objects.all(),
        "total": totals["total"],
        "available": totals["available"],
    }
    return render(request, "homepage/index.html", context)
