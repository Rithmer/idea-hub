from contextlib import closing

import pytest
from django.test import Client
from django.urls import reverse

import storage
from db import database


@pytest.mark.parametrize("route, title", [
    ("catalog:available", "Свободные идеи"),
    ("catalog:selected", "Выбранные идеи"),
    ("catalog:authors", "Авторы"),
    ("catalog:statistics", "Статистика"),
])
def test_sql_scenarios_and_navigation(route, title):
    response = Client().get(reverse(route))
    html = response.content.decode()
    assert response.status_code == 200
    assert title in html
    assert 'href="/ideas/statistics/"' in html
    assert 'href="/ideas/authors/"' in html
    assert html.count('aria-current="page"') == 1
    assert "SELECT " not in html
    assert "password" not in html


def test_web_reads_current_sqlite_values_without_loading_json(monkeypatch):
    with closing(database.get_connection()) as conn:
        conn.execute("UPDATE ideas SET title = ? WHERE id = 1", ("Актуальное название из SQLite",))
        conn.commit()

    def forbid_json(*args, **kwargs):
        raise AssertionError("Web views must query SQLite rather than JSON")

    monkeypatch.setattr(storage, "load_json", forbid_json)
    client = Client()
    for url in ["/", "/ideas/", "/ideas/1/", "/categories/1/", "/ideas/available/"]:
        assert "Актуальное название из SQLite" in client.get(url).content.decode()


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


@pytest.mark.parametrize("url, values", [
    ("/ideas/", {"category": "x"}),
    ("/ideas/", {"author": "-1"}),
    ("/ideas/", {"page": "0"}),
    ("/ideas/", {"page": "1000001"}),
    ("/ideas/", {"sort": "DROP TABLE ideas"}),
    ("/ideas/", {"status": "invalid"}),
    ("/ideas/", {"q": "a" * 201}),
    ("/ideas/available/", {"category": "1 OR 1=1"}),
    ("/ideas/statistics/", {"minimum": "-1"}),
    ("/ideas/statistics/", {"minimum": "abc"}),
])
def test_invalid_parameters_return_clear_400(url, values):
    response = Client().get(url, values)
    assert response.status_code == 400
    assert "Проверьте параметры поиска" in response.content.decode()


@pytest.mark.parametrize("q", ["' OR 1=1 --", "%; DROP TABLE ideas; --", "<script>alert(1)</script>"])
def test_user_search_is_literal_parameterized_and_escaped(q):
    response = Client().get("/ideas/", {"q": q})
    html = response.content.decode()
    assert response.status_code == 200
    assert "Найдено идей: 0" in html
    assert "<script>alert(1)</script>" not in html
    assert Client().get("/ideas/1/").status_code == 200


def test_sorting_and_pagination_preserve_filters():
    with closing(database.get_connection()) as conn:
        conn.executemany("""
            INSERT INTO ideas (id, title, description, category_id, author_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [(100 + i, f"Pagination {i:02}", "Test description", 1, 2, "2026-10-15")
              for i in range(14)])
        conn.commit()
    client = Client()
    first = client.get("/ideas/", {"q": "Pagination", "category": 1, "sort": "title"})
    second = client.get("/ideas/", {"q": "Pagination", "category": 1, "sort": "title", "page": 2})
    first_html, second_html = first.content.decode(), second.content.decode()
    assert "Pagination 00" in first_html and "Pagination 11" in first_html
    assert "Pagination 12" not in first_html
    assert "Pagination 12" in second_html and "Pagination 13" in second_html
    assert "Pagination 00" not in second_html
    assert "q=Pagination&amp;category=1&amp;sort=title&amp;page=2" in first_html
    assert client.get("/ideas/", {"page": 999}).status_code == 404
    oldest = client.get("/ideas/", {"sort": "oldest"}).content.decode()
    assert oldest.index("Платформа для обмена книгами") < oldest.index("Трекер привычек")


def test_statistics_thresholds_and_empty_database():
    client = Client()
    response = client.get("/ideas/statistics/", {"minimum": 3})
    assert response.status_code == 200
    assert "Нет категорий с таким количеством идей." in response.content.decode()
    with closing(database.get_connection()) as conn:
        conn.execute("DELETE FROM ideas")
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM categories")
        conn.commit()
    for url in ["/", "/ideas/", "/categories/", "/ideas/available/", "/ideas/selected/",
                "/ideas/authors/", "/ideas/statistics/"]:
        assert client.get(url).status_code == 200
    assert "Пока никто не выбрал идею." in client.get("/ideas/selected/").content.decode()
    assert "Пока нет авторов." in client.get("/ideas/authors/").content.decode()
