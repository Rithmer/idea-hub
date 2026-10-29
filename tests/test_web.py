"""Проверки страниц, связанных данных, ошибок и экранирования текста."""
import pytest
from django.test import override_settings

from catalog.models import Idea
from taxonomy.models import Category


@pytest.mark.parametrize("url, title", [
    ("/", "IdeaHub"),
    ("/ideas/", "Идеи для проектов"),
    ("/categories/", "Категории"),
])
def test_main_pages_and_navigation(client, url, title):
    response = client.get(url)
    html = response.content.decode()
    assert response.status_code == 200
    assert title in html
    assert 'href="/ideas/"' in html
    assert 'href="/categories/"' in html


def test_detail_pages_show_related_data(client):
    idea = client.get("/ideas/2/")
    category = client.get("/categories/3/")
    assert idea.status_code == category.status_code == 200
    assert "Трекер привычек" in idea.content.decode()
    assert "JavaScript" in idea.content.decode()
    assert "Иван Петров" in idea.content.decode()
    assert "Взята" in idea.content.decode()
    assert 'href="/ideas/2/"' in category.content.decode()


@pytest.mark.parametrize("url", [
    "/ideas/999/", "/categories/999/", "/ideas/not-an-id/", "/nonexistent/",
])
@override_settings(DEBUG=False)
def test_missing_pages_return_404(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert "не найден" in response.content.decode()


def test_idea_page_escapes_text_and_formats_date(client):
    Idea.objects.filter(pk=1).update(
        title="<script>alert(1)</script>",
        description="Первая строка\nВторая строка", created_at="2026-10-01",
    )
    Category.objects.filter(pk=1).update(name="<Python>")
    response = client.get("/ideas/1/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;Python&gt;" in html
    assert "Первая строка<br>Вторая строка" in html
    assert "01.10.2026" in html


def test_category_without_ideas(client):
    response = client.get("/categories/5/")
    assert response.status_code == 200
    assert "Go" in response.content.decode()
    assert "В этой категории пока нет идей." in response.content.decode()
