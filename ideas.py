from datetime import date
from typing import Any

Idea = dict[str, Any]
AVAILABLE = "не взята"
TAKEN = "взята"


def get_idea_by_id(ideas: list[Idea], idea_id: int) -> Idea | None:
    return next((idea for idea in ideas if idea["id"] == idea_id), None)


def add_idea(
    ideas: list[Idea], title: str, description: str, category: str,
    author: str, created_at: date,
) -> Idea:
    next_id = max((idea["id"] for idea in ideas), default=0) + 1
    idea: Idea = {
        "id": next_id, "title": title.strip(),
        "description": description.strip(), "category": category.strip(),
        "author": author.strip(), "status": AVAILABLE, "selected_by": None,
        "created_at": created_at.isoformat(),
    }
    ideas.append(idea)
    return idea


def find_ideas(ideas: list[Idea], query: str = "") -> list[Idea]:
    normalized_query = query.strip().casefold()
    return [
        idea for idea in ideas
        if (
            not normalized_query
            or normalized_query in idea["title"].casefold()
            or normalized_query in idea["category"].casefold()
        )
    ]


def filter_ideas_by_category(ideas: list[Idea], category: str) -> list[Idea]:
    normalized_category = category.strip().casefold()
    if not normalized_category:
        return ideas.copy()
    return [
        idea for idea in ideas
        if idea["category"].casefold() == normalized_category
    ]


def filter_ideas_by_status(ideas: list[Idea], status: str) -> list[Idea]:
    statuses = {
        "свободные": AVAILABLE,
        "не взята": AVAILABLE,
        "взятые": TAKEN,
        "взята": TAKEN,
    }
    selected_status = statuses.get(status.strip().casefold())
    if selected_status is None:
        return ideas.copy()
    return [idea for idea in ideas if idea["status"] == selected_status]


def sort_ideas(ideas: list[Idea]) -> list[Idea]:
    return sorted(ideas, key=lambda idea: (idea["category"], idea["title"]))


def is_idea_available(ideas: list[Idea], idea_id: int) -> bool:
    idea = get_idea_by_id(ideas, idea_id)
    return idea is not None and idea["status"] == AVAILABLE


def select_idea(ideas: list[Idea], idea_id: int, user_name: str) -> Idea:
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    if not is_idea_available(ideas, idea_id):
        raise ValueError("идея уже взята")
    if not user_name.strip():
        raise ValueError("имя пользователя не может быть пустым")
    idea["status"] = TAKEN
    idea["selected_by"] = user_name.strip()
    return idea


def cancel_selection(ideas: list[Idea], idea_id: int) -> Idea:
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    if idea["status"] == AVAILABLE:
        raise ValueError("идея уже свободна")
    idea["status"] = AVAILABLE
    idea["selected_by"] = None
    return idea


def get_statistics(ideas: list[Idea]) -> dict[str, Any]:
    by_category: dict[str, int] = {}
    for idea in ideas:
        category = idea["category"]
        by_category[category] = by_category.get(category, 0) + 1
    return {
        "total": len(ideas),
        "available": sum(idea["status"] == AVAILABLE for idea in ideas),
        "taken": sum(idea["status"] == TAKEN for idea in ideas),
        "by_category": dict(sorted(by_category.items())),
    }
