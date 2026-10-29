# IdeaHub — каталог идей программных проектов

Учебный проект для поиска идей по языкам программирования, просмотра авторов,
выбранных проектов и статистики. ПР9: переход с SQLite-запросов на Django ORM.

## Технологии

- Python 3.11+, Django 5.2.
- SQLite, Django ORM, Django Templates.
- pytest, flake8, Django Debug Toolbar.

## Запуск проекта

Команды выполняются из корня проекта.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py import_pr7
python manage.py runserver
```

В Windows PowerShell активация: `.venv\Scripts\Activate.ps1`.
Сайт: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Базы данных

Веб-приложение работает с `db.sqlite3` в корне проекта через Django ORM.
Таблицы создаются командой `python manage.py migrate`. Рабочая база исключена
из Git; после клонирования её нужно создать и наполнить.

`data/idea_hub.sqlite` — сохранённая исходная база ПР7, включённая в репозиторий.
Команда `python manage.py import_pr7` читает её и переносит данные в пустые
таблицы `db.sqlite3`, сохраняя идентификаторы и связи. Исходная база не меняется.
Повторный перенос в непустые таблицы запрещён, чтобы не перезаписать данные.

Если проект уже запускался, для обновления достаточно `python manage.py migrate`:
повторно выполнять импорт не нужно.

## Модели данных

- `Category` — язык программирования; поля: `id`, `name`.
- `User` — участник; поля: `id`, `name`, `password` (хеш), `is_admin`.
- `Idea` — идея; поля: `id`, `title`, `description`, `status`, `created_at`;
  связи `ForeignKey`: `category`, `author`, необязательный `selected_by`.

Обратные связи: `category.ideas`, `user.authored_ideas`, `user.selected_ideas`.
Удаление связанных объектов защищено `PROTECT`. Ограничения БД согласуют статус
с выбором участника и разрешают участнику выбрать не более одной идеи.
`participants.User` хранит участников ПР7 отдельно от Django auth.
При выделении приложения `participants` сохранена таблица `catalog_user`:
миграции меняют принадлежность модели и связи в состоянии Django,
не удаляя пользователей и не пересоздавая таблицы.

## Структура проекта

- `catalog/` — модель идеи, ORM-запросы, параметры поиска,
  представления, шаблоны и команды переноса и демонстрации.
- `participants/` — модель участника и миграции её переноса из каталога.
- `taxonomy/` — модель категории, представления и шаблоны категорий.
- `homepage/` — главная страница.
- `idea_hub/` — настройки и маршруты; `*/migrations/` — миграции моделей.
- `templates/`, `static/` — общие шаблоны и оформление.
- `data/`, `db/`, `sql/` — исходные данные и SQL-слой ПР7.
- `main.py`, `models.py`, `storage.py` — консольная версия; `tests/` — тесты веб-приложения.

## Страницы

- `/` — главная; `/ideas/` — каталог с поиском, фильтрами, сортировкой и пагинацией.
- `/ideas/<id>/`, `/categories/<id>/` — подробные страницы.
- `/categories/` — категории; `/ideas/authors/` — авторы.
- `/ideas/available/`, `/ideas/selected/` — свободные и выбранные идеи.
- `/ideas/statistics/` — статистика.

```bash
python manage.py seed_demo  # Добавить 12 идей для демонстрации пагинации
python manage.py demo_orm   # Показать CRUD с откатом изменений
```

## Проверки

```bash
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check --dry-run
pytest -q
flake8 .
```

Тесты проверяют страницы, поиск, фильтры, сортировку, пагинацию, статистику,
ошибки и экранирование пользовательского текста. Для них создаётся отдельная
тестовая база с данными через ORM; рабочая база не изменяется.
