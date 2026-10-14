import json
import os
from typing import NoReturn

import django
from django.http import Http404, HttpRequest
from django.test import Client, override_settings
from django.urls import include, path

from db import database
from db.import_json import import_json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_hub.settings")
django.setup()


def raise_not_found(request: HttpRequest) -> NoReturn:
    raise Http404("Private exception details")


handler404 = "homepage.views.page_not_found"
urlpatterns = [
    path("missing/", raise_not_found),
    path("", include("idea_hub.urls")),
]


def test_main_pages_and_navigation() -> None:
    client = Client()
    for url, title in [
        ("/", "IdeaHub"),
        ("/ideas/", "Идеи для проектов"),
        ("/categories/", "Категории"),
    ]:
        response = client.get(url)
        html = response.content.decode()
        assert response.status_code == 200
        assert title in html
        assert 'lang="ru"' in html
        assert "bootstrap@5.3.3" in html
        assert 'href="/ideas/"' in html
        assert 'href="/categories/"' in html


def test_detail_pages_use_linked_pr3_objects() -> None:
    client = Client()
    idea = client.get("/ideas/2/")
    category = client.get("/categories/3/")
    assert idea.status_code == category.status_code == 200
    assert "Трекер привычек" in idea.content.decode()
    assert "JavaScript" in idea.content.decode()
    assert "Иван Петров" in idea.content.decode()
    assert "Взята" in idea.content.decode()
    assert 'href="/ideas/2/"' in category.content.decode()


def test_missing_objects_return_404() -> None:
    client = Client()
    assert client.get("/ideas/999/").status_code == 404
    assert client.get("/categories/999/").status_code == 404
    assert client.get("/ideas/not-an-id/").status_code == 404


@override_settings(DEBUG=False)
def test_unmatched_urls_use_custom_404_page() -> None:
    client = Client()
    for url in ["/nonexistent/", "/ideas/not-an-id/", "/categories/not-an-id/"]:
        response = client.get(url)
        html = response.content.decode()
        assert response.status_code == 404
        assert "404 – страница не найдена" in html
        assert "Проверьте адрес или вернитесь на главную." in html
        assert 'class="btn btn-primary">На главную</a>' in html
        assert "IdeaHub" in html
        assert 'href="/static/css/site.css"' in html


@override_settings(DEBUG=False, ROOT_URLCONF=__name__)
def test_http404_uses_custom_page_without_exception_details() -> None:
    response = Client().get("/missing/")
    html = response.content.decode()
    assert response.status_code == 404
    assert "404 – страница не найдена" in html
    assert "Private exception details" not in html


def test_idea_page_reads_sqlite_and_escapes_text(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "escaping.sqlite")
    (tmp_path / "categories.json").write_text(
        json.dumps([{"id": 1, "name": "<Python>"}]), encoding="utf-8"
    )
    (tmp_path / "users.json").write_text(json.dumps([
        {"id": 1, "name": "Автор", "password": "unused"}
    ]), encoding="utf-8")
    (tmp_path / "ideas.json").write_text(json.dumps([{
        "id": 7,
        "title": "<script>alert(1)</script>",
        "description": "Новая идея",
        "category_id": 1,
        "author_id": 1,
        "status": "не взята",
        "selected_by_id": None,
        "created_at": "2026-10-01",
    }]), encoding="utf-8")
    import_json(tmp_path)
    client = Client()
    response = client.get("/ideas/7/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Новая идея" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html
    assert "&lt;Python&gt;" in html
