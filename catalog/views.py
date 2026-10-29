"""Представления каталога, проверка параметров и постраничный вывод."""
from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from catalog import queries
from catalog.models import Idea
from participants.models import User
from catalog.parameters import SearchParameters, integer_parameter
from taxonomy.models import Category


PAGE_SIZE = 12
SORT_ORDERS = queries.SORT_ORDERS


def search_context(search: SearchParameters) -> dict[str, Any]:
    """Готовит контекст формы из уже проверенных параметров поиска."""
    return {
        "q": search.q,
        "category_id": search.category_id,
        "author_id": search.author_id,
        "categories": Category.objects.all(),
    }


def invalid_search(request: HttpRequest, message: str) -> HttpResponse:
    """Возвращает страницу с пояснением ошибки ввода и HTTP-статусом 400."""
    return render(request, "catalog/invalid_search.html", {"message": message}, status=400)


def ideas(request: HttpRequest) -> HttpResponse:
    """Показывает каталог с фильтрами, сортировкой и сохранением параметров пагинации."""
    try:
        search = SearchParameters.from_query(request.GET)
        status = request.GET.get("status", "")
        sort = request.GET.get("sort", "newest")
        if status and status not in Idea.Status.values:
            raise ValueError("Выберите доступный статус.")
        if sort not in SORT_ORDERS:
            raise ValueError("Выберите доступный порядок сортировки.")
    except ValueError as error:
        return invalid_search(request, str(error))
    listing = queries.filtered_ideas(
        q=search.q, category=search.category_id,
        author=search.author_id, status=status,
    ).order_by(*SORT_ORDERS[sort])
    paginator = Paginator(listing, PAGE_SIZE)
    try:
        page = paginator.page(request.GET.get("page") or 1)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        return render(request, "404.html", status=404)
    context = search_context(search)
    context.update({
        "authors": User.objects.values("id", "name").order_by("name", "pk"),
        "ideas": page.object_list, "page_obj": page, "status": status, "sort": sort,
        "total": paginator.count, "statuses": Idea.Status.choices,
        "is_filtered": search.is_filtered or bool(status),
    })
    return render(request, "catalog/idea_list.html", context)


def idea_detail(request: HttpRequest, idea_id: int) -> HttpResponse:
    """Показывает идею со связанными объектами или возвращает страницу 404."""
    try:
        idea = get_object_or_404(queries.idea_listing(), pk=idea_id)
    except Http404:
        return render(request, "catalog/idea_not_found.html", status=404)
    return render(request, "catalog/idea_detail.html", {"idea": idea, "created_at": idea.created_at})


def available_ideas(request: HttpRequest) -> HttpResponse:
    """Показывает свободные идеи с поиском по названию, описанию и категории."""
    try:
        search = SearchParameters.from_query(request.GET)
    except ValueError as error:
        return invalid_search(request, str(error))
    context = search_context(search)
    context["ideas"] = queries.available_ideas(search.q, search.category_id)
    return render(request, "catalog/available.html", context)


def selected_ideas(request: HttpRequest) -> HttpResponse:
    """Показывает занятые идеи и выбравших их участников."""
    return render(request, "catalog/selected.html", {"ideas": queries.selected_ideas()})


def authors(request: HttpRequest) -> HttpResponse:
    """Показывает участников и количество опубликованных ими идей."""
    return render(request, "catalog/authors.html", {"authors": queries.author_statistics()})


def statistics(request: HttpRequest) -> HttpResponse:
    """Показывает сводные показатели и категории, прошедшие заданный порог."""
    try:
        minimum = integer_parameter(request.GET, "minimum", 2, minimum=0)
    except ValueError as error:
        return invalid_search(request, str(error))
    context = {
        "totals": queries.idea_totals(),
        "user_totals": queries.user_totals(),
        "category_statistics": queries.category_statistics(),
        "author_statistics": queries.author_statistics(),
        "popular_categories": queries.popular_categories(minimum),
        "status_statistics": queries.status_statistics(),
        "minimum": minimum,
    }
    return render(request, "catalog/statistics.html", context)
