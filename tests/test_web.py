"""Проверки веб-слоя ПР5 поверх JSON-данных ПР3."""
import json
import os

import django
from django.test import Client

import web_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_hub.settings")
django.setup()


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


def test_idea_page_reads_json_and_escapes_text(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(web_data, "DATA_DIR", tmp_path)
    (tmp_path / "categories.json").write_text(
        json.dumps([{"id": 1, "name": "<Python>"}]), encoding="utf-8"
    )
    (tmp_path / "users.json").write_text("[]", encoding="utf-8")
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
    client = Client()
    response = client.get("/ideas/7/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Новая идея" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html
    assert "&lt;Python&gt;" in html
