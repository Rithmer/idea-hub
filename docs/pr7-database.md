# SQLite в IdeaHub: ПР7

## Запуск

Готовая база предметной области включена в репозиторий: `data/idea_hub.sqlite`.
Она отдельна от служебной базы Django `db.sqlite3`.

```bash
python -m db.database
python -m db.import_json
python manage.py runserver
```

`python -m db.database` применяет схему `sql/schema.sql`, не удаляя данные.
`python -m db.import_json` переносит три исходных JSON-файла: категории,
пользователей, затем идеи. Повторный импорт обновляет записи с теми же ID
и добавляет новые без дубликатов. Дополнительные записи, созданные в SQLite,
автоматически не удаляются. Все вставки и обновления выполняются одной транзакцией:
ошибка в любом наборе данных откатывает изменения всех трёх таблиц.

Для отдельной базы можно указать свои пути:

```bash
python -m db.import_json --data-dir data --database /tmp/idea-hub-demo.sqlite
```

Исходные JSON-файлы и консольная реализация сохранены. Веб-часть читает SQLite;
консольная версия работает с JSON. Между ними нет автоматической синхронизации:
изменения JSON переносятся явным запуском импорта. Django ORM не используется.

## Таблицы, поля и ключи

| Таблица | Поля |
| --- | --- |
| `categories` | `id INTEGER PRIMARY KEY`, `name TEXT NOT NULL UNIQUE` |
| `users` | `id INTEGER PRIMARY KEY`, `name TEXT NOT NULL UNIQUE`, `password TEXT NOT NULL`, `is_admin INTEGER NOT NULL DEFAULT 0` |
| `ideas` | `id INTEGER PRIMARY KEY`, `title TEXT NOT NULL`, `description TEXT NOT NULL`, `category_id INTEGER NOT NULL`, `author_id INTEGER NOT NULL`, `status TEXT NOT NULL DEFAULT 'не взята'`, `selected_by_id INTEGER NULL`, `created_at TEXT NOT NULL` |

Внешние ключи: `ideas.category_id → categories.id`,
`ideas.author_id → users.id`, `ideas.selected_by_id → users.id`.
`selected_by_id` может быть `NULL` только у свободной идеи.
Даты импорта проверяются в Python и хранятся как `YYYY-MM-DD`.

CHECK-ограничения допускают только два статуса и значения 0/1 для признака
администратора. У выбранной идеи обязателен пользователь, у свободной — его
отсутствие. Частичный уникальный индекс запрещает одному пользователю выбрать
несколько идей. Индексы добавлены для категории, автора, статуса и даты создания.

Каждое соединение включает `PRAGMA foreign_keys = ON` и `sqlite3.Row`.
Веб-запросы открывают существующую базу только для чтения. Соединения закрываются
после выборки, а результаты доступны по именам полей. Пароли и административные
признаки не включаются в запросы для веб-страниц.

## Запросы и страницы

В `sql/queries.sql` находятся 17 именованных запросов. `db/queries.py` читает
эти же SQL-команды и выполняет их с параметрами `?`; SQL не дублируется в views.

| Запрос | Назначение и использование |
| --- | --- |
| `categories` | Список языков; главная страница и формы поиска |
| `users` | Список публичных имён для фильтра по автору |
| `ideas` | Каталог с категориями, авторами и участниками; JOIN, LIMIT, OFFSET |
| `idea_detail` | Подробная информация об идее по ID; JOIN, WHERE |
| `filtered_ideas` | Поиск по буквальному фрагменту названия, категории, автору, статусу; сортировка и пагинация |
| `available_ideas` | Свободные идеи по названию и языку |
| `selected_ideas` | Выбранные идеи с именами участников |
| `category_detail` | Категория по ID |
| `category_ideas` | Идеи конкретной категории |
| `idea_totals` | COUNT, SUM, MIN, MAX: количество, доступность, диапазон дат |
| `user_totals` | Количество авторов и участников с выбранной идеей |
| `category_statistics` | LEFT JOIN, COUNT, GROUP BY: идеи по языкам, включая пустые категории |
| `author_statistics` | LEFT JOIN, COUNT, GROUP BY: вклад каждого автора |
| `popular_categories` | GROUP BY и HAVING: категории с заданным минимумом идей |
| `status_statistics` | GROUP BY и COUNT: распределение по статусам |
| `recent_ideas` | ORDER BY и LIMIT: последние идеи на главной |
| `filtered_count` | Количество результатов поиска для пагинации |

Таким образом, выполнен минимум «10 запросов, по два каждого вида»:
списки (`categories`, `users`), WHERE (`filtered_ideas`, `available_ideas`),
JOIN (`ideas`, `idea_detail`), агрегаты (`idea_totals`, `user_totals`),
GROUP BY (`category_statistics`, `author_statistics`).
Результаты всех 17 запросов используются веб-интерфейсом.

Основные сценарии:

1. Каталог и комбинированный поиск: `/ideas/?q=Трекер&category=1`.
2. Поиск свободной идеи: `/ideas/available/?category=1`.
3. Просмотр выбранных идей и участников: `/ideas/selected/`.
4. Авторы и переход к их проектам: `/ideas/authors/`.
5. Статистика и фильтр групп: `/ideas/statistics/?minimum=2`.
6. Сведения об идее и категории: `/ideas/2/`, `/categories/3/`.
7. Главная страница с общими показателями и недавно добавленными идеями: `/`.

Пример Roomly адаптирован к предметной области IdeaHub: идеи не бронируются
на дату, поэтому поиск свободных объектов выполняется по текущему статусу,
языку и названию. Поиск фрагмента названия буквальный, с учётом регистра;
сортировки — сначала новые, сначала старые или по названию.
На странице каталога выводится по 12 идей. Параметры фильтров сохраняются
при переходе между страницами. Неверные параметры дают 400 с понятным
сообщением, отсутствующий объект или страница пагинации — 404.

## Проверка в SQLite CLI

Сводка фактического запуска всех запросов находится в `docs/pr7-sql-results.md`.
Пример параметризованного запроса для выбранных категорий:

```bash
sqlite3 -readonly data/idea_hub.sqlite
```

```sql
.headers on
.mode column
.parameter init
.parameter set ?1 2
SELECT c.id, c.name, COUNT(i.id) AS count
FROM categories AS c
LEFT JOIN ideas AS i ON i.category_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(i.id) >= ?1
ORDER BY count DESC, c.name, c.id;
PRAGMA integrity_check;
PRAGMA foreign_key_check;
.quit
```

Результат при исходных данных: Python, 2 идеи; целостность — `ok`, нарушений
внешних ключей нет. Категории C# и Go остаются в общей статистике с нулём идей.

## Проверки проекта

```bash
python manage.py check
pytest -v
flake8 . --extend-exclude=venv
mypy .
```

Тесты используют изолированные временные базы и не изменяют демонстрационный файл.
Проверены ограничения, повторный импорт, откат ошибочного импорта, связанные данные,
агрегаты, HAVING, пустые результаты, фильтры, сортировка, пагинация, параметры,
SQL-инъекции и отображение изменений SQLite без чтения JSON.

README по просьбе автора не изменён.
