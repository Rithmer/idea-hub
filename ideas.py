"""Поиск и управление идеями в консольной версии каталога."""
from models import Category, Idea, Status, User, today


def get_idea_by_id(ideas: list[Idea], idea_id: int) -> Idea | None:
    """Находит идею по идентификатору или возвращает None."""
    return next((idea for idea in ideas if idea.id == idea_id), None)


def add_idea(ideas: list[Idea], title: str, description: str, category_id: int,
             author_id: int, category: Category | None = None,
             author: User | None = None) -> Idea:
    """Создаёт свободную идею с новым идентификатором и текущей датой."""
    if not title.strip() or not description.strip():
        raise ValueError("название и описание не могут быть пустыми")
    idea = Idea(max((item.id for item in ideas), default=0) + 1, title.strip(),
                description.strip(), category_id, author_id, Status.AVAILABLE,
                None, today())
    ideas.append(idea)
    idea.category = category
    idea.author = author
    return idea


def edit_idea(ideas: list[Idea], idea_id: int, title: str, description: str,
              category_id: int, category: Category | None = None) -> Idea:
    """Обновляет название, описание и категорию существующей идеи."""
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    idea.edit(title, description, category if category is not None else category_id)
    return idea


def delete_idea(ideas: list[Idea], idea_id: int) -> None:
    """Удаляет идею из списка; при отсутствии вызывает ValueError."""
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    ideas.remove(idea)


def find_ideas(ideas: list[Idea], categories: list[Category], query: str = "") -> list[Idea]:
    """Ищет без учёта регистра по названию идеи и категории."""
    normalized = query.strip().casefold()
    names = {category.id: category.name.casefold() for category in categories}
    return [idea for idea in ideas if not normalized
            or normalized in idea.title.casefold()
            or normalized in names.get(idea.category_id, "")]


def filter_ideas(ideas: list[Idea], category_id: int | None,
                 status: Status | None) -> list[Idea]:
    """Отбирает идеи по необязательным условиям категории и статуса."""
    return [idea for idea in ideas if (category_id is None
            or idea.category_id == category_id) and (status is None
            or idea.status == status)]


def sort_ideas(ideas: list[Idea], categories: list[Category]) -> list[Idea]:
    """Сортирует идеи по названию категории, затем по названию идеи."""
    names = {category.id: category.name for category in categories}
    return sorted(ideas, key=lambda idea: (names.get(idea.category_id, ""), idea.title))


def select_idea(ideas: list[Idea], idea_id: int, user_id: int | User) -> Idea:
    """Закрепляет свободную идею за участником, у которого ещё нет выбранной идеи."""
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    if not idea.is_available:
        raise ValueError("идея уже взята")
    selected_by_id = user_id.id if isinstance(user_id, User) else user_id
    if any(item.selected_by_id == selected_by_id for item in ideas):
        raise ValueError("пользователь уже выбрал идею")
    idea.select(user_id)
    return idea


def cancel_selection(ideas: list[Idea], idea_id: int, user_id: int | User,
                     is_admin: bool = False) -> Idea:
    """Освобождает идею по запросу выбравшего участника или администратора."""
    idea = get_idea_by_id(ideas, idea_id)
    if idea is None:
        raise ValueError("идея не найдена")
    idea.release(user_id, is_admin)
    return idea


def get_user_idea(ideas: list[Idea], user_id: int) -> Idea | None:
    """Возвращает выбранную участником идею или None."""
    return next((idea for idea in ideas if idea.selected_by_id == user_id), None)


def get_statistics(ideas: list[Idea], categories: list[Category]) -> dict[str, object]:
    """Подсчитывает идеи по статусам и категориям."""
    by_category = {category.name: sum(idea.category_id == category.id for idea in ideas)
                   for category in categories}
    return {"total": len(ideas),
            "available": sum(idea.status is Status.AVAILABLE for idea in ideas),
            "taken": sum(idea.status is Status.TAKEN for idea in ideas),
            "by_category": dict(sorted(by_category.items()))}
