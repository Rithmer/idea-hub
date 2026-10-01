"""Адаптер JSON-хранилища ПР3 для страниц Django."""
from pathlib import Path

from models import Category, Idea, User
from storage import load_categories, load_ideas, load_users


DATA_DIR = Path(__file__).resolve().parent / "data"


def load_project_data() -> tuple[list[Idea], list[Category], list[User]]:
    """Загрузить сущности и восстановить связи объектной модели."""
    categories = load_categories(DATA_DIR / "categories.json")
    users = load_users(DATA_DIR / "users.json")
    ideas = load_ideas(DATA_DIR / "ideas.json")
    for idea in ideas:
        idea.bind(categories, users)
    return ideas, categories, users
