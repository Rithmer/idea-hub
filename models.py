"""Объектные модели консольной версии и преобразование данных JSON."""
from datetime import date
from enum import StrEnum

from passwords import ALGORITHM, hash_password, verify_password


def as_int(value: object, field_name: str) -> int:
    """Преобразует целое число или его строковую запись, отклоняя логические значения."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as error:
            raise ValueError(f"поле {field_name} должно быть целым числом") from error
    raise ValueError(f"поле {field_name} должно быть целым числом")


def as_bool(value: object, field_name: str) -> bool:
    """Принимает только логическое значение; иначе вызывает ValueError."""
    if isinstance(value, bool):
        return value
    raise ValueError(f"поле {field_name} должно быть true или false")


class Status(StrEnum):
    """Допустимые статусы идеи в консольной версии."""

    AVAILABLE = "не взята"
    TAKEN = "взята"


class User:
    """Пользователь консольной версии с паролем и признаком администратора."""

    def __init__(self, id: int, name: str, password: str,
                 is_admin: bool = False) -> None:
        self.id = id
        self.name = name
        self.password = password
        self.is_admin = is_admin

    def __str__(self) -> str:
        return f"{self.name} ({'администратор' if self.is_admin else 'пользователь'})"

    def set_password(self, password: str) -> None:
        """Заменяет сохранённый пароль его хешем PBKDF2."""
        self.password = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль и при успешном входе обновляет прежний формат хранения."""
        if not verify_password(self.password, password):
            return False
        if not self.password.startswith(f"{ALGORITHM}$"):
            self.set_password(password)
        return True

    def to_dict(self) -> dict[str, object]:
        """Возвращает поля объекта в формате для сохранения в JSON."""
        return {"id": self.id, "name": self.name, "password": self.password,
                "is_admin": self.is_admin}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "User":
        """Создаёт объект из словаря, проверяя типы идентификаторов и остальных полей."""
        return cls(as_int(data["id"], "id"), str(data["name"]),
                   str(data["password"]),
                   as_bool(data.get("is_admin", False), "is_admin"))


class Category:
    """Категория консольного каталога с идентификатором и названием."""

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return self.name

    def rename(self, name: str) -> None:
        """Задаёт непустое название категории без крайних пробелов."""
        if not name.strip():
            raise ValueError("название категории не может быть пустым")
        self.name = name.strip()

    def to_dict(self) -> dict[str, object]:
        """Возвращает поля объекта в формате для сохранения в JSON."""
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Category":
        """Создаёт объект из словаря, проверяя типы идентификаторов и остальных полей."""
        return cls(as_int(data["id"], "id"), str(data["name"]))


class Idea:
    """Идея консольного каталога с идентификаторами и восстановленными объектными связями."""

    def __init__(self, id: int, title: str, description: str, category_id: int,
                 author_id: int, status: Status, selected_by_id: int | None,
                 created_at: str) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.category_id = category_id
        self.author_id = author_id
        self.status = status
        self.selected_by_id = selected_by_id
        self.created_at = created_at
        self.category: Category | None = None
        self.author: User | None = None
        self.selected_by: User | None = None

    def __str__(self) -> str:
        category = str(self.category) if self.category else str(self.category_id)
        return f"[{self.id}] {self.title} ({category}) — {self.status.value}"

    @property
    def is_available(self) -> bool:
        """Проверяет, свободна ли идея для выбора участником."""
        return self.status is Status.AVAILABLE

    def select(self, user: User | int) -> None:
        """Закрепляет свободную идею за участником; занятую идею отклоняет."""
        if not self.is_available:
            raise ValueError("идея уже взята")
        self.status = Status.TAKEN
        self.selected_by_id = user.id if isinstance(user, User) else user
        self.selected_by = user if isinstance(user, User) else None

    def release(self, user: User | int, is_admin: bool = False) -> None:
        """Освобождает идею, проверяя права выбравшего участника или администратора."""
        if self.is_available:
            raise ValueError("идея уже свободна")
        user_id = user.id if isinstance(user, User) else user
        if not is_admin and self.selected_by_id != user_id:
            raise ValueError("можно отменить только свой выбор")
        self.status = Status.AVAILABLE
        self.selected_by_id = None
        self.selected_by = None

    def edit(self, title: str, description: str, category: Category | int) -> None:
        """Проверяет и обновляет название, описание и категорию идеи."""
        if not title.strip() or not description.strip():
            raise ValueError("название и описание не могут быть пустыми")
        self.title = title.strip()
        self.description = description.strip()
        self.category_id = category.id if isinstance(category, Category) else category
        self.category = category if isinstance(category, Category) else None

    def bind(self, categories: list[Category], users: list[User]) -> None:
        """Восстанавливает объектные связи категории, автора и выбравшего участника по ID."""
        self.category = next((item for item in categories
                              if item.id == self.category_id), None)
        self.author = next((item for item in users
                            if item.id == self.author_id), None)
        self.selected_by = next((item for item in users
                                 if item.id == self.selected_by_id), None)

    def to_dict(self) -> dict[str, object]:
        """Возвращает поля объекта в формате для сохранения в JSON."""
        return {"id": self.id, "title": self.title,
                "description": self.description, "category_id": self.category_id,
                "author_id": self.author_id, "status": self.status.value,
                "selected_by_id": self.selected_by_id, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Idea":
        """Создаёт объект из словаря, проверяя типы идентификаторов и остальных полей."""
        selected = data.get("selected_by_id")
        return cls(as_int(data["id"], "id"), str(data["title"]),
                   str(data["description"]), as_int(data["category_id"], "category_id"),
                   as_int(data["author_id"], "author_id"), Status(str(data["status"])),
                   None if selected is None else as_int(selected, "selected_by_id"),
                   str(data["created_at"]))


def today() -> str:
    """Возвращает текущую дату в формате YYYY-MM-DD."""
    return date.today().isoformat()
