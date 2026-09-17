from datetime import date
from pathlib import Path
from typing import Any

from ideas import (
    add_idea,
    cancel_selection,
    filter_ideas_by_category,
    filter_ideas_by_status,
    find_ideas,
    get_idea_by_id,
    get_statistics,
    select_idea,
    sort_ideas,
)
from storage import load_categories, load_ideas, save_categories, save_ideas
from utils import input_int, input_nonempty, print_idea, print_ideas

DATA_DIR = Path(__file__).parent / "data"
IDEAS_FILE = DATA_DIR / "ideas.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"

INITIAL_CATEGORIES = ["Python", "Java", "JavaScript", "C#", "Go"]
INITIAL_IDEAS = [
    {"id": 1, "title": "Приложение для поиска волонтёрских проектов",
     "description": "Сервис для поиска инициатив рядом с пользователем.",
     "category": "Python", "author": "Анна Смирнова",
     "status": "не взята", "selected_by": None, "created_at": "2026-09-09"},
    {"id": 2, "title": "Трекер привычек с геймификацией",
     "description": "Приложение для отслеживания привычек с очками.",
     "category": "JavaScript", "author": "Иван Петров", "status": "взята",
     "selected_by": "Иван Петров", "created_at": "2026-09-05"},
    {"id": 3, "title": "Платформа для обмена книгами",
     "description": "Сервис для бесплатного обмена книгами между соседями.",
     "category": "Java", "author": "Мария Кузнецова",
     "status": "не взята", "selected_by": None, "created_at": "2026-08-28"},
    {"id": 4, "title": "Трекер расходов для студентов",
     "description": "Приложение для учёта расходов и планирования стипендии.",
     "category": "Python", "author": "Дмитрий Соколов", "status": "не взята",
     "selected_by": None, "created_at": "2026-09-01"},
]


def initialize_data() -> tuple[list[dict[str, Any]], list[str]]:
    categories = load_categories(CATEGORIES_FILE)
    ideas = load_ideas(IDEAS_FILE)
    if not categories:
        categories = INITIAL_CATEGORIES.copy()
        save_categories(CATEGORIES_FILE, categories)
    if not ideas:
        ideas = INITIAL_IDEAS.copy()
        save_ideas(IDEAS_FILE, ideas)
    return ideas, categories


def show_menu() -> None:
    print("\n===== IdeaHub: каталог проектных идей =====")
    print("1. Показать каталог\n2. Найти идеи\n3. Подробная информация")
    print("4. Добавить идею\n5. Выбрать свободную идею")
    print("6. Отказаться от выбранной идеи\n7. Добавить категорию")
    print("8. Показать статистику\n0. Выход")


def choose_category(categories: list[str]) -> str:
    print("Доступные категории:")
    for number, category in enumerate(categories, start=1):
        print(f"{number}. {category}")
    choice = input_nonempty("Номер категории или новое название: ")
    if choice.isdigit() and 1 <= int(choice) <= len(categories):
        return categories[int(choice) - 1]
    normalized = choice.casefold()
    if normalized not in {item.casefold() for item in categories}:
        categories.append(choice)
        print(f"Категория «{choice}» добавлена.")
    return next(item for item in categories if item.casefold() == normalized)


def handle_add_idea(
    ideas: list[dict[str, Any]], categories: list[str]
) -> None:
    idea = add_idea(
        ideas, input_nonempty("Название: "), input_nonempty("Описание: "),
        choose_category(categories), input_nonempty("Автор: "), date.today(),
    )
    print(f"Идея «{idea['title']}» добавлена с номером {idea['id']}.")


def handle_search(ideas: list[dict[str, Any]]) -> None:
    query = input("Поисковый запрос (Enter - все идеи): ")
    category = input(
        "Язык: Python / Java / JavaScript / C# / Go (Enter - все): "
    )
    status = input("Статус: свободные / взятые (Enter - все): ")
    results = find_ideas(ideas, query)
    results = filter_ideas_by_category(results, category)
    results = filter_ideas_by_status(results, status)
    print_ideas(sort_ideas(results))


def handle_select(ideas: list[dict[str, Any]]) -> None:
    try:
        idea = select_idea(ideas, input_int("Номер идеи: "),
                           input_nonempty("Ваше имя: "))
    except ValueError as error:
        print(f"Не удалось выбрать идею: {error}")
        return
    print(f"Идея «{idea['title']}» закреплена за {idea['selected_by']}.")


def handle_cancel(ideas: list[dict[str, Any]]) -> None:
    try:
        idea = cancel_selection(ideas, input_int("Номер идеи: "))
    except ValueError as error:
        print(f"Не удалось отменить выбор: {error}")
        return
    print(f"Идея «{idea['title']}» снова свободна.")


def handle_details(ideas: list[dict[str, Any]]) -> None:
    idea = get_idea_by_id(ideas, input_int("Номер идеи: "))
    if idea is None:
        print("Идея с таким номером не найдена.")
        return
    print_idea(idea, detailed=True)


def show_statistics(ideas: list[dict[str, Any]]) -> None:
    statistics = get_statistics(ideas)
    print(f"Всего идей: {statistics['total']}")
    print(f"Свободных: {statistics['available']}")
    print(f"Взятых: {statistics['taken']}\nПо категориям:")
    for category, count in statistics["by_category"].items():
        print(f"- {category}: {count}")


def main() -> None:
    ideas, categories = initialize_data()
    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("Выход из программы.")
            return
        if choice == "1":
            print_ideas(sort_ideas(ideas))
        elif choice == "2":
            handle_search(ideas)
        elif choice == "3":
            handle_details(ideas)
        elif choice == "4":
            handle_add_idea(ideas, categories)
        elif choice == "5":
            handle_select(ideas)
        elif choice == "6":
            handle_cancel(ideas)
        elif choice == "7":
            choose_category(categories)
        elif choice == "8":
            show_statistics(ideas)
        else:
            print("Неверный пункт меню.")
            continue
        save_ideas(IDEAS_FILE, ideas)
        save_categories(CATEGORIES_FILE, categories)


if __name__ == "__main__":
    main()
