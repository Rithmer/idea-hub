"""Проверки ORM-страниц, фильтрации, сортировки и пагинации."""
import pytest
from django.test import Client
from django.urls import reverse

from catalog.models import Idea
from participants.models import User
from taxonomy.models import Category


@pytest.mark.parametrize("route, title", [
    ("catalog:available", "Свободные идеи"),
    ("catalog:selected", "Выбранные идеи"),
    ("catalog:authors", "Авторы"),
    ("catalog:statistics", "Статистика"),
])
def test_orm_scenarios_and_navigation(route, title):
    response = Client().get(reverse(route))
    html = response.content.decode()
    assert response.status_code == 200
    assert title in html
    assert 'href="/ideas/statistics/"' in html
    assert 'href="/ideas/authors/"' in html
    assert html.count('aria-current="page"') == 1


def test_pages_show_updated_idea():
    Idea.objects.filter(pk=1).update(title="Обновлённая идея")
    client = Client()
    for url in ["/", "/ideas/", "/ideas/1/", "/categories/1/", "/ideas/available/"]:
        response = client.get(url)
        assert response.status_code == 200
        assert "Обновлённая идея" in response.content.decode()


def test_search_combines_filters_and_preserves_user_selection():
    response = Client().get("/ideas/", {
        "q": "Трекер", "category": 1, "author": 5, "status": "не взята", "sort": "title",
    })
    html = response.content.decode()
    assert response.status_code == 200
    assert "Трекер расходов для студентов" in html
    assert "Трекер привычек с геймификацией" not in html
    assert "Найдено идей: 1" in html
    assert 'value="Трекер"' in html
    assert 'value="1" selected' in html
    assert 'value="5" selected' in html
    assert 'value="не взята" selected' in html
    assert 'value="title" selected' in html


def test_available_and_selected_ideas():
    client = Client()
    available = client.get("/ideas/available/", {"category": 1}).content.decode()
    assert "Приложение для поиска волонтёрских проектов" in available
    assert "Трекер расходов для студентов" in available
    assert "Трекер привычек с геймификацией" not in available
    assert "Свободных идей по выбранным условиям нет." in client.get(
        "/ideas/available/", {"category": 3}
    ).content.decode()
    selected = client.get("/ideas/selected/").content.decode()
    assert "Трекер привычек с геймификацией" in selected
    assert "Выбрал: Иван Петров" in selected
    assert "Трекер расходов для студентов" not in selected


@pytest.mark.parametrize("query", ["инициатив", "Python"])
def test_available_search_matches_description_and_category(client, query):
    response = client.get("/ideas/available/", {"q": query})
    assert response.status_code == 200
    assert "Приложение для поиска волонтёрских проектов" in response.content.decode()
    assert "Трекер привычек с геймификацией" not in response.content.decode()


def test_statistics_and_authors_show_catalog_counts(client):
    response = client.get("/ideas/statistics/")
    assert response.status_code == 200
    assert response.context["totals"]["total"] == 4
    assert response.context["totals"]["available"] == 3
    assert response.context["totals"]["taken"] == 1
    assert response.context["user_totals"] == {"authors": 4, "selectors": 1}
    assert [(row.name, row.count) for row in response.context["popular_categories"]] == [("Python", 2)]
    assert "Python" in response.content.decode()
    authors = client.get("/ideas/authors/")
    assert authors.status_code == 200
    assert "Анна Смирнова" in authors.content.decode()
    assert {row.name: row.count for row in authors.context["authors"]} == {
        "Администратор": 0, "Анна Смирнова": 1, "Иван Петров": 1,
        "Мария Кузнецова": 1, "Дмитрий Соколов": 1,
    }


@pytest.mark.parametrize("url, values", [
    ("/ideas/", {"category": "x"}),
    ("/ideas/", {"author": "-1"}),
    ("/ideas/", {"sort": "unknown"}),
    ("/ideas/", {"status": "invalid"}),
    ("/ideas/", {"q": "a" * 201}),
    ("/ideas/available/", {"category": "abc"}),
    ("/ideas/statistics/", {"minimum": "-1"}),
    ("/ideas/statistics/", {"minimum": "abc"}),
])
def test_invalid_parameters_return_clear_400(url, values):
    response = Client().get(url, values)
    assert response.status_code == 400
    assert "Проверьте параметры поиска" in response.content.decode()


@pytest.mark.parametrize("field", ["category", "author"])
def test_unknown_filter_id_returns_empty_catalog(field):
    response = Client().get("/ideas/", {field: "999999"})
    assert response.status_code == 200
    assert "Найдено идей: 0" in response.content.decode()


def test_empty_parameters_keep_defaults_and_search_is_trimmed():
    response = Client().get("/ideas/", {
        "q": "  Трекер  ", "category": "", "author": "", "page": "",
    })
    html = response.content.decode()
    assert response.status_code == 200
    assert "Найдено идей: 2" in html
    assert 'value="Трекер"' in html


@pytest.mark.parametrize("page", ["abc", "1.5", ""])
def test_invalid_page_opens_first_page_with_filters(page):
    parameters = {"q": "Трекер", "category": 1, "sort": "title"}
    client = Client()
    first = client.get("/ideas/", parameters)
    response = client.get("/ideas/", {**parameters, "page": page})
    assert response.status_code == 200
    assert response.content == first.content


@pytest.mark.parametrize("page", [0, -1, 999, 1000001])
def test_missing_page_returns_404(page):
    assert Client().get("/ideas/", {"page": page}).status_code == 404


def test_sorting_and_pagination_preserve_filters():
    Idea.objects.bulk_create([
        Idea(id=100 + i, title=f"Pagination {i:02}", description="Test description",
             category_id=1, author_id=2, created_at="2026-10-15") for i in range(14)
    ])
    client = Client()
    first = client.get("/ideas/", {"q": "Pagination", "category": 1, "sort": "title"})
    second = client.get("/ideas/", {"q": "Pagination", "category": 1, "sort": "title", "page": 2})
    first_html, second_html = first.content.decode(), second.content.decode()
    assert "Pagination 00" in first_html and "Pagination 11" in first_html
    assert "Pagination 12" not in first_html
    assert "Pagination 12" in second_html and "Pagination 13" in second_html
    assert "Pagination 00" not in second_html
    assert "q=Pagination&amp;category=1&amp;sort=title&amp;page=2" in first_html
    assert "q=Pagination&amp;category=1&amp;sort=title&amp;page=1" in second_html
    assert "Предыдущая" not in first_html
    assert "Следующая" not in second_html
    assert client.get("/ideas/", {"page": 999}).status_code == 404
    oldest = client.get("/ideas/", {"sort": "oldest"}).content.decode()
    assert oldest.index("Платформа для обмена книгами") < oldest.index("Трекер привычек")


def test_statistics_thresholds_and_empty_database():
    client = Client()
    response = client.get("/ideas/statistics/", {"minimum": 3})
    assert response.status_code == 200
    assert "Нет категорий с таким количеством идей." in response.content.decode()
    Idea.objects.all().delete()
    User.objects.all().delete()
    Category.objects.all().delete()
    for url in ["/", "/ideas/", "/categories/", "/ideas/available/", "/ideas/selected/",
                "/ideas/authors/", "/ideas/statistics/"]:
        assert client.get(url).status_code == 200
    assert "Пока никто не выбрал идею." in client.get("/ideas/selected/").content.decode()
    assert "Пока нет авторов." in client.get("/ideas/authors/").content.decode()
