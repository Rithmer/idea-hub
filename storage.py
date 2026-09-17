import json
from pathlib import Path
from typing import Any


def load_json(filename: Path) -> list[Any]:
    try:
        with filename.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename.name} не найден. Будет создан новый.")
        return []
    except json.JSONDecodeError:
        print(f"Файл {filename.name} содержит некорректный JSON.")
        return []
    except OSError as error:
        print(f"Не удалось прочитать {filename.name}: {error}")
        return []
    if not isinstance(data, list):
        print(f"Файл {filename.name} должен содержать список.")
        return []
    return data


def save_json(filename: Path, data: list[Any]) -> None:
    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Не удалось сохранить {filename.name}: {error}")


def load_ideas(filename: Path) -> list[dict[str, Any]]:
    return [item for item in load_json(filename) if isinstance(item, dict)]


def save_ideas(filename: Path, ideas: list[dict[str, Any]]) -> None:
    save_json(filename, ideas)


def load_categories(filename: Path) -> list[str]:
    return [item for item in load_json(filename) if isinstance(item, str)]


def save_categories(filename: Path, categories: list[str]) -> None:
    save_json(filename, categories)
