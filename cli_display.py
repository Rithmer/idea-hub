from ideas import get_user_idea
from models import Idea, User
from utils import print_idea


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
