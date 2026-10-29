"""Проверка параметров поиска независимо от HTTP-ответов и ORM-запросов."""
from collections.abc import Mapping
from dataclasses import dataclass
from typing import overload


MAX_PARAMETER_VALUE = 1_000_000
MAX_QUERY_LENGTH = 200


@overload
def integer_parameter(parameters: Mapping[str, str], name: str,
                      default: int, *, minimum: int = 1) -> int: ...


@overload
def integer_parameter(parameters: Mapping[str, str], name: str,
                      default: None = None, *, minimum: int = 1) -> int | None: ...


def integer_parameter(parameters: Mapping[str, str], name: str,
                      default: int | None = None, *, minimum: int = 1) -> int | None:
    """Читает целое число в допустимом диапазоне; пустое значение заменяет default."""
    value = parameters.get(name, "")
    if not value:
        return default
    try:
        result = int(value)
    except ValueError as error:
        raise ValueError(f"Укажите целое число в параметре {name}.") from error
    if not minimum <= result <= MAX_PARAMETER_VALUE:
        raise ValueError(f"Недопустимое значение параметра {name}.")
    return result


@dataclass(frozen=True)
class SearchParameters:
    """Параметры поиска после нормализации строки и проверки идентификаторов."""

    q: str
    category_id: int | None
    author_id: int | None

    @classmethod
    def from_query(cls, parameters: Mapping[str, str]) -> "SearchParameters":
        """Преобразует GET-параметры; неизвестный корректный ID даёт пустую выборку."""
        q = parameters.get("q", "").strip()
        if len(q) > MAX_QUERY_LENGTH:
            raise ValueError(f"Поисковый запрос не должен превышать {MAX_QUERY_LENGTH} символов.")
        return cls(q=q, category_id=integer_parameter(parameters, "category"),
                   author_id=integer_parameter(parameters, "author"))

    @property
    def is_filtered(self) -> bool:
        """Проверяет наличие хотя бы одного условия поиска."""
        return bool(self.q or self.category_id or self.author_id)
