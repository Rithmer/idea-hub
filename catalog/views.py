from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ideas import get_idea_by_id
from web_data import load_project_data


def ideas(request: HttpRequest) -> HttpResponse:
    context = {"ideas": load_project_data().ideas}
    return render(request, "catalog/idea_list.html", context)


def idea_detail(request: HttpRequest, idea_id: int) -> HttpResponse:
    idea = get_idea_by_id(load_project_data().ideas, idea_id)
    if idea is None:
        return render(request, "catalog/idea_not_found.html", status=404)
    try:
        created_at = date.fromisoformat(idea.created_at)
    except ValueError:
        created_at = None
    context = {"idea": idea, "created_at": created_at}
    return render(request, "catalog/idea_detail.html", context)
