from categories import get_category_by_id
from cli_admin import choose_category, manage_categories, manage_ideas
from cli_display import show_profile
from ideas import (add_idea, cancel_selection, filter_ideas, find_ideas,
                   get_idea_by_id, get_statistics, select_idea,
                   sort_ideas)
from models import Category, Idea, Status, User
from utils import input_int, input_nonempty, print_idea, print_ideas


def perform_action(choice: str, user: User, ideas: list[Idea],
                   categories: list[Category], users: list[User]) -> bool:
    if choice == "1":
        print_ideas(sort_ideas(ideas, categories))
    elif choice == "2":
        found = find_ideas(ideas, categories, input("Запрос: "))
        status = input("Статус: свободные/взятые (Enter - все): ").strip()
        selected_status = {"свободные": Status.AVAILABLE, "взятые": Status.TAKEN}.get(status)
        print_ideas(filter_ideas(found, None, selected_status))
    elif choice == "3":
        idea = get_idea_by_id(ideas, input_int("Номер идеи: "))
        if idea is None:
            raise ValueError("идея не найдена")
        print_idea(idea, detailed=True)
    elif choice == "4":
        title = input_nonempty("Название: ")
        description = input_nonempty("Описание: ")
        category_id = choose_category(categories)
        add_idea(ideas, title, description, category_id, user.id,
                 get_category_by_id(categories, category_id), user)
    elif choice == "5":
        select_idea(ideas, input_int("Номер идеи: "), user)
    elif choice == "6":
        cancel_selection(ideas, input_int("Номер идеи: "), user, user.is_admin)
    elif choice == "7":
        print(get_statistics(ideas, categories))
    elif choice == "8":
        show_profile(user, ideas)
    elif choice == "10" and user.is_admin:
        manage_ideas(ideas, categories, user)
    elif choice == "11" and user.is_admin:
        manage_categories(categories, ideas)
    elif choice == "12" and user.is_admin:
        for item in users:
            print(f"[{item.id}] {item.name} ({'админ' if item.is_admin else 'пользователь'})")
    else:
        print("Неверный пункт меню или недостаточно прав.")
        return False
    return True
