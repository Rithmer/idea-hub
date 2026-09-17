"""Вспомогательные функции ввода и отображения данных."""

from datetime import date
from typing import Any


def input_nonempty(prompt: str) -> str:
    """Запросить непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым.")


def input_int(prompt: str) -> int:
    """Запросить целое число, повторяя ввод при ошибке."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить дату в формате ГГГГ-ММ-ДД."""
    while True:
        try:
            return date.fromisoformat(input(prompt).strip())
        except ValueError:
            print("Введите дату в формате ГГГГ-ММ-ДД.")


def print_idea(idea: dict[str, Any], detailed: bool = False) -> None:
    """Вывести краткую или подробную информацию об идее."""
    print(f"[{idea['id']}] {idea['title']} ({idea['category']})")
    print(f"Статус: {idea['status']}")
    if detailed:
        print(f"Описание: {idea['description']}")
        print(f"Автор: {idea['author']}")
        print(f"Выбрал: {idea['selected_by'] or '—'}")
        print(f"Дата создания: {idea['created_at']}")


def print_ideas(ideas: list[dict[str, Any]]) -> None:
    """Вывести список идей или сообщение о пустом результате."""
    if not ideas:
        print("Идей по заданным условиям не найдено.")
        return
    for idea in ideas:
        print_idea(idea)
