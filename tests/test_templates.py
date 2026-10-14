"""Regression checks for the PR6 template migration."""
import json
import os

import django
import pytest
from django.contrib.staticfiles import finders
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import resolve, reverse

import web_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_hub.settings")
django.setup()


@pytest.fixture
def template_client():
    setup_test_environment()
    try:
        yield Client()
    finally:
        teardown_test_environment()


@pytest.mark.parametrize("url, template, context_key, namespace", [
    ("/", "homepage/index.html", "ideas", "homepage"),
    ("/ideas/", "catalog/idea_list.html", "ideas", "catalog"),
    ("/ideas/2/", "catalog/idea_detail.html", "idea", "catalog"),
    ("/categories/", "taxonomy/category_list.html", "category_cards", "taxonomy"),
    ("/categories/3/", "taxonomy/category_detail.html", "category", "taxonomy"),
])
def test_pages_render_templates_and_context(template_client, url, template,
                                            context_key, namespace):
    response = template_client.get(url)
    assert response.status_code == 200
    templates = {item.name for item in response.templates}
    assert {template, "base.html", "includes/navigation.html"} <= templates
    assert response.context[context_key] is not None
    assert resolve(url).namespace == namespace
    html = response.content.decode()
    assert html.count('aria-current="page"') == 1
    assert "/static/homepage/img/logo.svg" in html
    assert "/static/homepage/js/main.js" in html
    assert 'id="current-year"' in html


def test_named_urls_and_static_files():
    assert reverse("homepage:index") == "/"
    assert reverse("catalog:ideas") == "/ideas/"
    assert reverse("catalog:idea_detail", args=[2]) == "/ideas/2/"
    assert reverse("taxonomy:categories") == "/categories/"
    assert reverse("taxonomy:category_detail", args=[3]) == "/categories/3/"
    for name in ["css/site.css", "homepage/img/logo.svg", "homepage/js/main.js"]:
        assert finders.find(name) is not None


def write_data(tmp_path, monkeypatch, categories, ideas):
    monkeypatch.setattr(web_data, "DATA_DIR", tmp_path)
    for filename, value in [("categories", categories), ("ideas", ideas),
                            ("users", [])]:
        (tmp_path / f"{filename}.json").write_text(
            json.dumps(value), encoding="utf-8"
        )


def test_empty_lists_and_empty_category(tmp_path, monkeypatch):
    write_data(tmp_path, monkeypatch, [], [])
    client = Client()
    assert "Пока нет идей." in client.get("/ideas/").content.decode()
    assert "Пока нет категорий." in client.get("/categories/").content.decode()
    assert client.get("/").status_code == 200
    write_data(tmp_path, monkeypatch, [{"id": 1, "name": "Python"}], [])
    assert "В этой категории пока нет идей." in client.get("/categories/1/").content.decode()


@pytest.mark.parametrize("created_at, expected", [
    ("2026-10-01", "01.10.2026"), ("invalid-date", "Не указана"),
])
def test_filters_fallbacks_and_autoescaping(tmp_path, monkeypatch, created_at, expected):
    write_data(tmp_path, monkeypatch, [{"id": 1, "name": "<Python>"}], [{
        "id": 7, "title": "", "description": "<script>alert(1)</script>\nВторая строка",
        "category_id": 1, "author_id": 999, "status": "не взята",
        "selected_by_id": None, "created_at": created_at,
    }])
    client = Client()
    for url in ["/ideas/", "/ideas/7/", "/categories/1/"]:
        html = client.get(url).content.decode()
        assert "Без названия" in html
        assert "Свободна" in html
        assert "<script>alert(1)</script>" not in html
    detail = client.get("/ideas/7/").content.decode()
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>Вторая строка" in detail
    assert "&lt;Python&gt;" in detail
    assert "Неизвестен" in detail
    assert expected in detail
    assert "&lt;Python&gt;" in client.get("/categories/").content.decode()
    write_data(tmp_path, monkeypatch, [], [{
        "id": 7, "title": "Идея", "description": "Описание",
        "category_id": 999, "author_id": 999, "status": "не взята",
        "selected_by_id": None, "created_at": created_at,
    }])
    assert "Без категории" in client.get("/ideas/7/").content.decode()


def test_status_include_is_shared(template_client):
    for url in ["/ideas/", "/ideas/2/", "/categories/3/"]:
        response = template_client.get(url)
        assert "catalog/includes/idea_status.html" in {item.name for item in response.templates}
        assert "Взята" in response.content.decode()
    assert "Свободна" in template_client.get("/ideas/1/").content.decode()
