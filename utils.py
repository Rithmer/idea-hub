from models import Category, Idea, User


def input_nonempty(prompt: str) -> str:

    while not (value := input(prompt).strip()):
        print("Значение не может быть пустым.")
    return value


def input_int(prompt: str) -> int:

    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Введите целое число.")


def category_name(categories: list[Category], category_id: int) -> str:

    return next((item.name for item in categories if item.id == category_id), "—")


def user_name(users: list[User], user_id: int | None) -> str:

    return next((item.name for item in users if item.id == user_id), "—")


def print_idea(idea: Idea, categories: list[Category], users: list[User],
               detailed: bool = False) -> None:

    print(f"[{idea.id}] {idea.title} ({category_name(categories, idea.category_id)})")
    print(f"Статус: {idea.status.value}")
    if detailed:
        print(f"Описание: {idea.description}\nАвтор: {user_name(users, idea.author_id)}")
        print(f"Выбрал: {user_name(users, idea.selected_by_id)}")
        print(f"Дата создания: {idea.created_at}")


def print_ideas(ideas: list[Idea], categories: list[Category], users: list[User]) -> None:
    if not ideas:
        print("Идей по заданным условиям не найдено.")
        return
    for idea in ideas:
        print_idea(idea, categories, users)
