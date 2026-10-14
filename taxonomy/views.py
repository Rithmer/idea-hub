from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.queries import fetch_all, fetch_ideas, fetch_one


def categories(request: HttpRequest) -> HttpResponse:
    category_cards = [
        {"category": row, "count": row["count"]}
        for row in fetch_all("category_statistics")
    ]
    return render(request, "taxonomy/category_list.html",
                  {"category_cards": category_cards})


def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    category = fetch_one("category_detail", (category_id,))
    if category is None:
        return render(request, "taxonomy/category_not_found.html", status=404)
    context = {"category": category, "ideas": fetch_ideas("category_ideas", (category_id,))}
    return render(request, "taxonomy/category_detail.html", context)
