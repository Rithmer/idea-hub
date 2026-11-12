"""Проверка параметров поиска независимо от HTTP-ответов и ORM-запросов."""
from collections.abc import Mapping
from typing import overload


MAX_PARAMETER_VALUE = 1_000_000


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
