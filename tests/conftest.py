from pathlib import Path

import pytest

from db import database
from db.import_json import import_json


@pytest.fixture(autouse=True)
def sqlite_database(tmp_path, monkeypatch) -> Path:
    """Every test has its own database; the committed demonstration DB is never changed."""
    path = tmp_path / "test.sqlite"
    monkeypatch.setattr(database, "DB_PATH", path)
    import_json(db_path=path)
    return path
