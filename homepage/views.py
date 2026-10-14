from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_ideas, fetch_one


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def index(request: HttpRequest) -> HttpResponse:
    totals = fetch_one("idea_totals")
    context = {
        "ideas": fetch_ideas("recent_ideas", (3,)),
        "categories": fetch_all("categories"),
        "total": totals["total"] if totals is not None else 0,
        "available": totals["available"] if totals is not None else 0,
    }
    return render(request, "homepage/index.html", context)
