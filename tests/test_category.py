import pytest

from categories import add_category, delete_category, rename_category
from models import Category, Idea


def test_category_management() -> None:
    categories: list[Category] = []
    ideas: list[Idea] = []
    category = add_category(categories, "Python")
    assert rename_category(categories, category.id, "Python 3").name == "Python 3"
    with pytest.raises(ValueError, match="уже существует"):
        add_category(categories, "python 3")
    delete_category(categories, ideas, category.id)
    assert categories == []
