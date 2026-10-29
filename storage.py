"""Чтение, проверка и сохранение объектов консольной версии в JSON."""
import json
from pathlib import Path
from typing import Callable, Protocol, TypeVar

from models import Category, Idea, User


class JsonEntity(Protocol):
    """Протокол объекта, поддерживающего преобразование в словарь для JSON."""

    def to_dict(self) -> dict[str, object]:
        ...


Entity = TypeVar("Entity", bound=JsonEntity)


def load_json(filename: Path) -> list[dict[str, object]]:
    """Читает список словарей из JSON; отсутствующий файл означает пустой список."""
    try:
        with filename.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в {filename.name}") from error
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError(f"Файл {filename.name} должен содержать список объектов")
    return [dict(item) for item in data]


def save_entities(filename: Path, entities: list[Entity]) -> None:
    """Сохраняет словарные представления объектов в JSON с кодировкой UTF-8."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    payload = [entity.to_dict() for entity in entities]
    with filename.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_entities(filename: Path,
                  factory: Callable[[dict[str, object]], Entity]) -> list[Entity]:
    """Создаёт объекты из JSON; при ошибке указывает номер некорректной записи."""
    entities: list[Entity] = []
    for number, item in enumerate(load_json(filename), start=1):
        try:
            entities.append(factory(item))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"Некорректная запись {number} в {filename.name}: {error}"
            ) from error
    return entities


def load_users(filename: Path) -> list[User]:
    """Загружает пользователей из JSON и проверяет типы их полей."""
    return load_entities(filename, User.from_dict)


def load_categories(filename: Path) -> list[Category]:
    """Загружает категории из JSON и проверяет типы их полей."""
    return load_entities(filename, Category.from_dict)


def load_ideas(filename: Path) -> list[Idea]:
    """Загружает идеи из JSON и проверяет типы их полей."""
    return load_entities(filename, Idea.from_dict)
