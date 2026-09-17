from models import Category, Idea


def get_category_by_id(categories: list[Category], category_id: int) -> Category | None:
    return next((item for item in categories if item.id == category_id), None)


def add_category(categories: list[Category], name: str) -> Category:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("название категории не может быть пустым")
    if any(item.name.casefold() == clean_name.casefold() for item in categories):
        raise ValueError("такая категория уже существует")
    category = Category(max((item.id for item in categories), default=0) + 1,
                        clean_name)
    categories.append(category)
    return category


def rename_category(categories: list[Category], category_id: int, name: str) -> Category:
    category = get_category_by_id(categories, category_id)
    if category is None:
        raise ValueError("категория не найдена")
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("название категории не может быть пустым")
    if any(item.id != category_id and item.name.casefold() == clean_name.casefold()
           for item in categories):
        raise ValueError("такая категория уже существует")
    category.name = clean_name
    return category


def delete_category(categories: list[Category], ideas: list[Idea], category_id: int) -> None:
    category = get_category_by_id(categories, category_id)
    if category is None:
        raise ValueError("категория не найдена")
    if any(idea.category_id == category_id for idea in ideas):
        raise ValueError("нельзя удалить категорию, пока в ней есть идеи")
    categories.remove(category)
