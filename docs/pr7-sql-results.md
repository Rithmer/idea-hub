# Проверка SQL-запросов ПР7 в SQLite CLI

Все запросы выполнены из `sql/queries.sql` через `sqlite3 -readonly data/idea_hub.sqlite`.
Значения переданы через `.parameter set`; исходные таблицы не изменялись.

| Запрос | Параметры | Строк результата |
| --- | --- | --- |
| `categories` | `()` | 5 |
| `users` | `()` | 5 |
| `ideas` | `(12, 0)` | 4 |
| `idea_detail` | `(2,)` | 1 |
| `filtered_ideas` | `('Трекер', 'Трекер', None, None, None, None, '', '', 'newest', 'newest', 12, 0)` | 2 |
| `available_ideas` | `('', '', 1, 1)` | 2 |
| `selected_ideas` | `()` | 1 |
| `category_detail` | `(3,)` | 1 |
| `category_ideas` | `(3,)` | 1 |
| `idea_totals` | `()` | 1 |
| `user_totals` | `()` | 1 |
| `category_statistics` | `()` | 5 |
| `author_statistics` | `()` | 5 |
| `popular_categories` | `(2,)` | 1 |
| `status_statistics` | `()` | 2 |
| `recent_ideas` | `(3,)` | 3 |
| `filtered_count` | `('', '', None, None, None, None, '', '')` | 1 |

Контроль целостности: `PRAGMA integrity_check` → `ok`, `PRAGMA foreign_key_check` → пустой результат.

У базы 5 категорий, 5 пользователей, 4 идеи: 3 свободных и 1 выбранная.
Категории C# и Go участвуют в статистике с нулевым количеством идей благодаря LEFT JOIN.
