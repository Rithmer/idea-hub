-- IdeaHub: SQLite schema for PR7. Django's db.sqlite3 is a separate database.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1))
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'не взята' CHECK (status IN ('не взята', 'взята')),
    selected_by_id INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL,
    CHECK ((status = 'не взята' AND selected_by_id IS NULL)
        OR (status = 'взята' AND selected_by_id IS NOT NULL))
);

-- Each user can select only one idea, as in the existing domain logic.
CREATE UNIQUE INDEX IF NOT EXISTS one_selected_idea_per_user
    ON ideas(selected_by_id) WHERE selected_by_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ideas_category ON ideas(category_id);
CREATE INDEX IF NOT EXISTS ideas_author ON ideas(author_id);
CREATE INDEX IF NOT EXISTS ideas_status_date ON ideas(status, created_at);
