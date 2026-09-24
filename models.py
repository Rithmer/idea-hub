from datetime import date
from enum import StrEnum
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex


def as_int(value: object, field_name: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as error:
            raise ValueError(f"поле {field_name} должно быть целым числом") from error
    raise ValueError(f"поле {field_name} должно быть целым числом")


def as_bool(value: object, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"поле {field_name} должно быть true или false")


class Status(StrEnum):
    AVAILABLE = "не взята"
    TAKEN = "взята"


class User:
    def __init__(self, id: int, name: str, password: str,
                 is_admin: bool = False) -> None:
        self.id = id
        self.name = name
        self.password = password
        self.is_admin = is_admin

    def __str__(self) -> str:
        return f"{self.name} ({'администратор' if self.is_admin else 'пользователь'})"

    def set_password(self, password: str) -> None:
        salt = token_hex(16)
        digest = pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000)
        self.password = f"pbkdf2_sha256$200000${salt}${digest.hex()}"

    def check_password(self, password: str) -> bool:
        if not self.password.startswith("pbkdf2_sha256$"):
            if not compare_digest(self.password, password):
                return False
            # Старые записи ПР2 обновляются после успешного входа.
            self.set_password(password)
            return True
        try:
            _, rounds, salt, expected = self.password.split("$")
            digest = pbkdf2_hmac("sha256", password.encode(),
                                 bytes.fromhex(salt), int(rounds))
            return compare_digest(digest, bytes.fromhex(expected))
        except (ValueError, OverflowError):
            return False

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "name": self.name, "password": self.password,
                "is_admin": self.is_admin}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "User":
        return cls(as_int(data["id"], "id"), str(data["name"]),
                   str(data["password"]),
                   as_bool(data.get("is_admin", False), "is_admin"))


class Category:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return self.name

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("название категории не может быть пустым")
        self.name = name.strip()

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Category":
        return cls(as_int(data["id"], "id"), str(data["name"]))


class Idea:
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
        return self.status is Status.AVAILABLE

    def select(self, user: User) -> None:
        if not self.is_available:
            raise ValueError("идея уже взята")
        self.status = Status.TAKEN
        self.selected_by_id = user.id
        self.selected_by = user

    def release(self, user: User, is_admin: bool = False) -> None:
        if self.is_available:
            raise ValueError("идея уже свободна")
        if not is_admin and self.selected_by_id != user.id:
            raise ValueError("можно отменить только свой выбор")
        self.status = Status.AVAILABLE
        self.selected_by_id = None
        self.selected_by = None

    def edit(self, title: str, description: str, category: Category | int) -> None:
        if not title.strip() or not description.strip():
            raise ValueError("название и описание не могут быть пустыми")
        self.title = title.strip()
        self.description = description.strip()
        self.category_id = category.id if isinstance(category, Category) else category
        self.category = category if isinstance(category, Category) else None

    def bind(self, categories: list[Category], users: list[User]) -> None:
        self.category = next((item for item in categories
                              if item.id == self.category_id), None)
        self.author = next((item for item in users
                            if item.id == self.author_id), None)
        self.selected_by = next((item for item in users
                                 if item.id == self.selected_by_id), None)

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "title": self.title,
                "description": self.description, "category_id": self.category_id,
                "author_id": self.author_id, "status": self.status.value,
                "selected_by_id": self.selected_by_id, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Idea":
        selected = data.get("selected_by_id")
        return cls(as_int(data["id"], "id"), str(data["title"]),
                   str(data["description"]), as_int(data["category_id"], "category_id"),
                   as_int(data["author_id"], "author_id"), Status(str(data["status"])),
                   None if selected is None else as_int(selected, "selected_by_id"),
                   str(data["created_at"]))


def today() -> str:
    return date.today().isoformat()
