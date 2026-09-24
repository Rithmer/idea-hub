import pytest

from storage import load_users, save_entities


@pytest.mark.parametrize(
    "content",
    ["{", '{"unexpected": "object"}', '[{"id": 1, "name": "Анна"}]'],
)
def test_invalid_user_data_is_not_treated_as_empty(tmp_path, content) -> None:
    filename = tmp_path / "users.json"
    filename.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        load_users(filename)
    assert filename.read_text(encoding="utf-8") == content


def test_save_failure_is_reported(tmp_path) -> None:
    filename = tmp_path / "directory"
    filename.mkdir()
    with pytest.raises(OSError):
        save_entities(filename, [])
