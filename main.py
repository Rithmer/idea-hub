from pathlib import Path

from categories import add_category, delete_category, get_category_by_id, rename_category
from ideas import (add_idea, cancel_selection, delete_idea, edit_idea, filter_ideas,
                   find_ideas, get_idea_by_id, get_statistics, get_user_idea,
                   select_idea, sort_ideas)
from models import Category, Idea, Status, User
from storage import (load_categories, load_ideas, load_users, save_entities)
from users import authenticate, register_user
from utils import input_int, input_nonempty, print_idea, print_ideas

DATA_DIR = Path(__file__).parent / "data"
IDEAS_FILE = DATA_DIR / "ideas.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
USERS_FILE = DATA_DIR / "users.json"


def load_data() -> tuple[list[Idea], list[Category], list[User]]:
    categories, users = load_categories(CATEGORIES_FILE), load_users(USERS_FILE)
    ideas = load_ideas(IDEAS_FILE)
    for idea in ideas:
        idea.bind(categories, users)
    return ideas, categories, users


def save_data(ideas: list[Idea], categories: list[Category], users: list[User]) -> None:
    save_entities(IDEAS_FILE, ideas)
    save_entities(CATEGORIES_FILE, categories)
    save_entities(USERS_FILE, users)


def choose_category(categories: list[Category]) -> int:
    for category in categories:
        print(f"{category.id}. {category.name}")
    category_id = input_int("Номер категории: ")
    if get_category_by_id(categories, category_id) is None:
        raise ValueError("категория не найдена")
    return category_id


def show_menu(user: User) -> None:
    print(f"\n=== IdeaHub | {user.name} ===")
    print("1. Каталог  2. Поиск  3. Детали  4. Добавить идею")
    print("5. Выбрать идею  6. Отказаться  7. Статистика  8. Профиль")
    print("9. Выйти из аккаунта  0. Завершить программу")
    if user.is_admin:
        print("10. Управлять идеями  11. Управлять категориями  12. Пользователи")


def show_profile(user: User, ideas: list[Idea]) -> None:
    print(f"Профиль: {user}; ID: {user.id}")
    print(f"Создано идей: {sum(idea.author_id == user.id for idea in ideas)}")
    idea = get_user_idea(ideas, user.id)
    if idea is None:
        print("Вы пока не выбрали идею.")
    else:
        print_idea(idea, detailed=True)


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


def authenticate_user(users: list[User]) -> User | None:
    while True:
        action = input("\n1. Войти  2. Регистрация  0. Выход: ").strip()
        if action == "0":
            return None
        if action == "2":
            try:
                registered_user = register_user(
                    users, input_nonempty("Имя: "), input_nonempty("Пароль: "))
                print(f"Пользователь «{registered_user.name}» создан. Теперь войдите.")
            except ValueError as error:
                print(error)
        elif action == "1":
            authenticated_user = authenticate(
                users, input_nonempty("Имя: "), input_nonempty("Пароль: "))
            if authenticated_user is not None:
                return authenticated_user
            print("Неверное имя или пароль.")
        else:
            print("Неверный пункт меню.")


def main() -> None:
    ideas, categories, users = load_data()
    while (user := authenticate_user(users)) is not None:
        save_data(ideas, categories, users)
        while True:
            show_menu(user)
            choice = input("Выберите действие: ").strip()
            try:
                if choice == "0":
                    save_data(ideas, categories, users)
                    return
                if choice == "9":
                    break
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
                    continue
                save_data(ideas, categories, users)
            except ValueError as error:
                print(f"Ошибка: {error}")
    save_data(ideas, categories, users)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"Ошибка данных: {error}") from error
