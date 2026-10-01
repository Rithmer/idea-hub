from pathlib import Path

from cli_actions import perform_action
from cli_auth import authenticate_user
from cli_display import show_menu
from models import Category, Idea, User
from storage import load_categories, load_ideas, load_users, save_entities


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
                if perform_action(choice, user, ideas, categories, users):
                    save_data(ideas, categories, users)
            except ValueError as error:
                print(f"Ошибка: {error}")
    save_data(ideas, categories, users)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"Ошибка данных: {error}") from error
