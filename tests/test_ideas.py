from datetime import date

import pytest

from ideas import (
    AVAILABLE,
    TAKEN,
    add_idea,
    cancel_selection,
    filter_ideas_by_category,
    filter_ideas_by_status,
    find_ideas,
    get_statistics,
    is_idea_available,
    select_idea,
    sort_ideas,
)


def make_ideas() -> list[dict]:
    ideas: list[dict] = []
    add_idea(ideas, "Python-трекер", "Описание", "Образование", "Анна",
             date(2026, 9, 1))
    add_idea(ideas, "Экосервис", "Описание", "Экология", "Иван",
             date(2026, 9, 2))
    return ideas


def test_add_idea_creates_available_idea() -> None:
    ideas = make_ideas()
    assert ideas[0]["id"] == 1
    assert ideas[0]["status"] == AVAILABLE


def test_find_and_sort_ideas() -> None:
    ideas = make_ideas()
    assert find_ideas(ideas, "python") == [ideas[0]]
    assert sort_ideas(ideas) == [ideas[0], ideas[1]]


def test_filters_by_category_and_status() -> None:
    ideas = make_ideas()
    select_idea(ideas, 1, "Студент")
    assert filter_ideas_by_category(ideas, "экология") == [ideas[1]]
    assert filter_ideas_by_status(ideas, "свободные") == [ideas[1]]


def test_selection_changes_availability() -> None:
    ideas = make_ideas()
    select_idea(ideas, 1, "Студент")
    assert ideas[0]["status"] == TAKEN
    assert not is_idea_available(ideas, 1)


def test_duplicate_selection_is_forbidden() -> None:
    ideas = make_ideas()
    select_idea(ideas, 1, "Студент")
    with pytest.raises(ValueError, match="уже взята"):
        select_idea(ideas, 1, "Другой студент")


def test_cancel_selection_and_statistics() -> None:
    ideas = make_ideas()
    select_idea(ideas, 1, "Студент")
    cancel_selection(ideas, 1)
    assert get_statistics(ideas)["available"] == 2
