import pytest

from ideas import add_idea, cancel_selection, select_idea
from models import Idea, Status


def test_idea_lifecycle() -> None:
    ideas: list[Idea] = []
    idea = add_idea(ideas, "Трекер", "Описание", 1, 10)
    assert idea.status is Status.AVAILABLE and idea.author_id == 10
    select_idea(ideas, idea.id, 20)
    assert idea.status is Status.TAKEN and idea.selected_by_id == 20
    with pytest.raises(ValueError, match="уже взята"):
        select_idea(ideas, idea.id, 30)
    cancel_selection(ideas, idea.id, 20)
    assert idea.status is Status.AVAILABLE and idea.selected_by_id is None


def test_user_cannot_select_two_ideas() -> None:
    ideas: list[Idea] = []
    first = add_idea(ideas, "Первая", "Описание", 1, 10)
    second = add_idea(ideas, "Вторая", "Описание", 1, 10)
    select_idea(ideas, first.id, 20)
    with pytest.raises(ValueError, match="уже выбрал"):
        select_idea(ideas, second.id, 20)
    assert second.is_available
