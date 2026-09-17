from ideas import add_idea, filter_ideas, select_idea
from models import Idea, Status


def test_status_filter() -> None:
    ideas: list[Idea] = []
    first = add_idea(ideas, "Первая", "Описание", 1, 1)
    add_idea(ideas, "Вторая", "Описание", 1, 1)
    select_idea(ideas, first.id, 2)
    assert filter_ideas(ideas, None, Status.AVAILABLE)[0].title == "Вторая"
    assert filter_ideas(ideas, None, Status.TAKEN) == [first]
