"""Адаптер JSON-хранилища ПР3 для страниц Django."""
from dataclasses import dataclass
from pathlib import Path

from models import Category, Idea
from storage import load_categories, load_ideas, load_users


DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class ProjectData:
    ideas: list[Idea]
    categories: list[Category]


def load_project_data() -> ProjectData:
    """Загрузить сущности и восстановить связи объектной модели."""
    categories = load_categories(DATA_DIR / "categories.json")
    users = load_users(DATA_DIR / "users.json")
    ideas = load_ideas(DATA_DIR / "ideas.json")
    for idea in ideas:
        idea.bind(categories, users)
    return ProjectData(ideas=ideas, categories=categories)
