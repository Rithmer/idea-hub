import json

import pytest

from ideas import add_idea, cancel_selection, select_idea
import main
from models import Category, Idea, Status, User
from storage import load_ideas, load_users, save_entities
from users import authenticate, register_user
from utils import print_idea


def test_object_relationships_survive_json_round_trip(tmp_path) -> None:
    category = Category(1, "Python")
    author = User(1, "Автор", "legacy")
    reader = User(2, "Читатель", "legacy")
    ideas: list[Idea] = []
    idea = add_idea(ideas, "Трекер", "Описание", category.id, author.id,
                    category, author)
    assert idea.category is category
    assert idea.author is author
    select_idea(ideas, idea.id, reader)
    assert idea.selected_by is reader
    filename = tmp_path / "ideas.json"
    save_entities(filename, ideas)
    payload = json.loads(filename.read_text(encoding="utf-8"))
    assert "category" not in payload[0]
    restored = load_ideas(filename)[0]
    restored.bind([category], [author, reader])
    assert restored.category is category
    assert restored.author is author
    assert restored.selected_by is reader
    assert restored.status is Status.TAKEN
    assert "Трекер" in str(restored)
    with pytest.raises(ValueError, match="свой выбор"):
        cancel_selection([restored], restored.id, author)
    cancel_selection([restored], restored.id, reader)
    assert restored.is_available
    assert restored.selected_by is None


def test_idea_output_uses_linked_objects(capsys) -> None:
    category = Category(1, "Python")
    author = User(1, "Автор", "secret")
    idea = add_idea([], "Трекер", "Описание", category.id, author.id,
                    category, author)
    print_idea(idea, detailed=True)
    output = capsys.readouterr().out
    assert "Python" in output
    assert "Автор" in output
    assert "Описание" in output


def test_registration_hashes_password_and_legacy_login_upgrades(tmp_path) -> None:
    users: list[User] = []
    registered = register_user(users, " Анна ", "secret")
    assert registered.password != "secret"
    assert authenticate(users, "анна", "wrong") is None
    assert authenticate(users, "анна", "secret") is registered
    filename = tmp_path / "users.json"
    save_entities(filename, users)
    restored = load_users(filename)
    assert authenticate(restored, "Анна", "secret") is restored[0]
    legacy = User(2, "Старый", "oldpass")
    assert authenticate([legacy], "Старый", "oldpass") is legacy
    assert legacy.password != "oldpass"


def test_category_and_idea_methods() -> None:
    category = Category(1, "Python")
    category.rename(" Java ")
    assert str(category) == "Java"
    idea = Idea(1, "Название", "Описание", 1, 1, Status.AVAILABLE, None,
                "2026-09-24")
    idea.edit(" Новое ", " Текст ", category)
    assert (idea.title, idea.description, idea.category) == ("Новое", "Текст", category)
    with pytest.raises(ValueError):
        idea.edit("", "Текст", category)


def test_registration_profile_logout_and_persistence(tmp_path, monkeypatch,
                                                     capsys) -> None:
    monkeypatch.setattr(main, "IDEAS_FILE", tmp_path / "ideas.json")
    monkeypatch.setattr(main, "CATEGORIES_FILE", tmp_path / "categories.json")
    monkeypatch.setattr(main, "USERS_FILE", tmp_path / "users.json")
    answers = iter(["2", "Анна", "secret", "1", "Анна", "secret",
                    "8", "9", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    main.main()
    output = capsys.readouterr().out
    assert "Профиль: Анна" in output
    assert "Вы пока не выбрали идею" in output
    saved = load_users(tmp_path / "users.json")
    assert len(saved) == 1
    assert saved[0].password != "secret"
