from dataclasses import asdict, dataclass
from datetime import date
from enum import StrEnum


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


@dataclass
class User:

    id: int
    name: str
    password: str
    is_admin: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "User":
        return cls(
            id=as_int(data["id"], "id"),
            name=str(data["name"]),
            password=str(data["password"]),
            is_admin=as_bool(data.get("is_admin", False), "is_admin"),
        )


@dataclass
class Category:

    id: int
    name: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Category":
        return cls(id=as_int(data["id"], "id"), name=str(data["name"]))


@dataclass
class Idea:

    id: int
    title: str
    description: str
    category_id: int
    author_id: int
    status: Status
    selected_by_id: int | None
    created_at: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Idea":
        selected_by_id = data.get("selected_by_id")
        return cls(
            id=as_int(data["id"], "id"),
            title=str(data["title"]),
            description=str(data["description"]),
            category_id=as_int(data["category_id"], "category_id"),
            author_id=as_int(data["author_id"], "author_id"),
            status=Status(str(data["status"])),
            selected_by_id=(None if selected_by_id is None else as_int(
                selected_by_id, "selected_by_id")),
            created_at=str(data["created_at"]),
        )


def today() -> str:

    return date.today().isoformat()
