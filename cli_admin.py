from categories import add_category, delete_category, get_category_by_id, rename_category
from ideas import cancel_selection, delete_idea, edit_idea, get_idea_by_id, select_idea
from models import Category, Idea, Status, User
from utils import input_int, input_nonempty


def choose_category(categories: list[Category]) -> int:
    for category in categories:
        print(f"{category.id}. {category.name}")
    category_id = input_int("Номер категории: ")
    if get_category_by_id(categories, category_id) is None:
        raise ValueError("категория не найдена")
    return category_id


def manage_categories(categories: list[Category], ideas: list[Idea]) -> None:
    action = input("Категории: 1-добавить, 2-переименовать, 3-удалить: ").strip()
    if action == "1":
        print(f"Добавлено: {add_category(categories, input_nonempty('Название: ')).name}")
    elif action == "2":
        rename_category(categories, input_int("Номер: "), input_nonempty("Новое название: "))
    elif action == "3":
        delete_category(categories, ideas, input_int("Номер: "))
    else:
        raise ValueError("неверное действие")


def manage_ideas(ideas: list[Idea], categories: list[Category], admin: User) -> None:
    action = input("Идеи: 1-изменить, 2-удалить, 3-изменить статус: ").strip()
    idea_id = input_int("Номер идеи: ")
    if action == "1":
        title = input_nonempty("Название: ")
        description = input_nonempty("Описание: ")
        category_id = choose_category(categories)
        edit_idea(ideas, idea_id, title, description, category_id,
                  get_category_by_id(categories, category_id))
    elif action == "2":
        delete_idea(ideas, idea_id)
    elif action == "3":
        idea = get_idea_by_id(ideas, idea_id)
        if idea is None:
            raise ValueError("идея не найдена")
        if idea.status is Status.AVAILABLE:
            select_idea(ideas, idea_id, admin)
        else:
            cancel_selection(ideas, idea_id, admin, is_admin=True)
    else:
        raise ValueError("неверное действие")
