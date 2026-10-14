from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from web_data import load_project_data


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def index(request: HttpRequest) -> HttpResponse:
    data = load_project_data()
    context = {
        "ideas": data.ideas,
        "categories": data.categories,
        "available": sum(idea.is_available for idea in data.ideas),
    }
    return render(request, "homepage/index.html", context)
