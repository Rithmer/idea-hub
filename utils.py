from models import Idea


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


def print_idea(idea: Idea, detailed: bool = False) -> None:
    print(idea)
    if detailed:
        print(f"Описание: {idea.description}")
        print(f"Автор: {idea.author or '—'}")
        print(f"Выбрал: {idea.selected_by or '—'}")
        print(f"Дата создания: {idea.created_at}")


def print_ideas(ideas: list[Idea]) -> None:
    if not ideas:
        print("Идей по заданным условиям не найдено.")
        return
    for idea in ideas:
        print_idea(idea)
