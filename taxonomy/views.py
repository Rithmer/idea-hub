from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from categories import get_category_by_id
from web_data import load_project_data


def categories(request: HttpRequest) -> HttpResponse:
    data = load_project_data()
    category_cards = [
        {"category": category,
         "count": sum(idea.category_id == category.id for idea in data.ideas)}
        for category in data.categories
    ]
    return render(request, "taxonomy/category_list.html",
                  {"category_cards": category_cards})


def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    data = load_project_data()
    category = get_category_by_id(data.categories, category_id)
    if category is None:
        return render(request, "taxonomy/category_not_found.html", status=404)
    context = {
        "category": category,
        "ideas": [idea for idea in data.ideas if idea.category_id == category_id],
    }
    return render(request, "taxonomy/category_detail.html", context)
