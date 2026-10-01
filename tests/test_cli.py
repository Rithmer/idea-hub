import main
from models import Category, User
from storage import load_categories, load_ideas, save_entities


def test_admin_cli_saves_category_and_idea(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(main, "IDEAS_FILE", tmp_path / "ideas.json")
    monkeypatch.setattr(main, "CATEGORIES_FILE", tmp_path / "categories.json")
    monkeypatch.setattr(main, "USERS_FILE", tmp_path / "users.json")
    save_entities(main.IDEAS_FILE, [])
    save_entities(main.CATEGORIES_FILE, [Category(1, "Python")])
    save_entities(main.USERS_FILE, [User(1, "Админ", "secret", is_admin=True)])
    answers = iter([
        "1", "Админ", "secret",
        "11", "1", "Go",
        "4", "Новая идея", "Описание", "2",
        "0",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    main.main()

    categories = load_categories(main.CATEGORIES_FILE)
    ideas = load_ideas(main.IDEAS_FILE)
    assert [(item.id, item.name) for item in categories] == [(1, "Python"), (2, "Go")]
    assert [(item.title, item.category_id, item.author_id) for item in ideas] == [
        ("Новая идея", 2, 1)
    ]
