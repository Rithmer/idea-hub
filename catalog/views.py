from datetime import date
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_ideas, fetch_one, present_idea


PAGE_SIZE = 12
STATUSES = ("", "не взята", "взята")
SORT_ORDERS = ("newest", "oldest", "title")


def integer_parameter(request: HttpRequest, name: str, default: int | None = None,
                      *, minimum: int = 1) -> int | None:
    value = request.GET.get(name, "")
    if not value:
        return default
    try:
        result = int(value)
    except ValueError as error:
        raise ValueError("Укажите целое число в параметре " + name + ".") from error
    if not minimum <= result <= 1_000_000:
        raise ValueError("Недопустимое значение параметра " + name + ".")
    return result


def search_context(request: HttpRequest) -> dict[str, Any]:
    q = request.GET.get("q", "").strip()
    if len(q) > 200:
        raise ValueError("Поисковый запрос не должен превышать 200 символов.")
    return {
        "q": q,
        "category_id": integer_parameter(request, "category"),
        "author_id": integer_parameter(request, "author"),
        "categories": fetch_all("categories"),
        "authors": fetch_all("users"),
    }


def invalid_search(request: HttpRequest, message: str) -> HttpResponse:
    return render(request, "catalog/invalid_search.html", {"message": message}, status=400)


def ideas(request: HttpRequest) -> HttpResponse:
    try:
        context = search_context(request)
        page_number = integer_parameter(request, "page", 1) or 1
        status = request.GET.get("status", "")
        sort = request.GET.get("sort", "newest")
        if status not in STATUSES or sort not in SORT_ORDERS:
            raise ValueError("Выберите доступный статус и порядок сортировки.")
    except ValueError as error:
        return invalid_search(request, str(error))
    q, category, author = context["q"], context["category_id"], context["author_id"]
    filters = (q, q, category, category, author, author, status, status)
    count = fetch_one("filtered_count", filters)
    total = count["count"] if count is not None else 0
    offset = (page_number - 1) * PAGE_SIZE
    if page_number > 1 and offset >= total:
        return render(request, "404.html", status=404)
    if q or category is not None or author is not None or status or sort != "newest":
        listing = fetch_ideas("filtered_ideas", filters + (sort, sort, PAGE_SIZE, offset))
    else:
        listing = fetch_ideas("ideas", (PAGE_SIZE, offset))
    previous_query = request.GET.copy()
    previous_query["page"] = str(page_number - 1)
    next_query = request.GET.copy()
    next_query["page"] = str(page_number + 1)
    context.update({
        "ideas": listing, "status": status, "sort": sort, "total": total,
        "page_number": page_number, "has_previous": page_number > 1,
        "has_next": offset + PAGE_SIZE < total,
        "previous_query": previous_query.urlencode(), "next_query": next_query.urlencode(),
        "is_filtered": bool(q or category or author or status),
    })
    return render(request, "catalog/idea_list.html", context)


def idea_detail(request: HttpRequest, idea_id: int) -> HttpResponse:
    row = fetch_one("idea_detail", (idea_id,))
    if row is None:
        return render(request, "catalog/idea_not_found.html", status=404)
    try:
        created_at = date.fromisoformat(row["created_at"])
    except ValueError:
        created_at = None
    context = {"idea": present_idea(row), "created_at": created_at}
    return render(request, "catalog/idea_detail.html", context)


def available_ideas(request: HttpRequest) -> HttpResponse:
    try:
        context = search_context(request)
    except ValueError as error:
        return invalid_search(request, str(error))
    q, category = context["q"], context["category_id"]
    context["ideas"] = fetch_ideas("available_ideas", (q, q, category, category))
    return render(request, "catalog/available.html", context)


def selected_ideas(request: HttpRequest) -> HttpResponse:
    return render(request, "catalog/selected.html", {"ideas": fetch_ideas("selected_ideas")})


def authors(request: HttpRequest) -> HttpResponse:
    return render(request, "catalog/authors.html", {"authors": fetch_all("author_statistics")})


def statistics(request: HttpRequest) -> HttpResponse:
    try:
        minimum = integer_parameter(request, "minimum", 2, minimum=0)
    except ValueError as error:
        return invalid_search(request, str(error))
    context = {
        "totals": fetch_one("idea_totals"),
        "user_totals": fetch_one("user_totals"),
        "category_statistics": fetch_all("category_statistics"),
        "author_statistics": fetch_all("author_statistics"),
        "popular_categories": fetch_all("popular_categories", (minimum,)),
        "status_statistics": fetch_all("status_statistics"),
        "minimum": minimum,
    }
    return render(request, "catalog/statistics.html", context)
