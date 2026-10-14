## Текущая реализация после ПР6

Веб-интерфейс IdeaHub использует Django Template Language (DTL).
Представления загружают объекты из JSON, готовят словарь контекста и вызывают
`render()`. HTML находится в шаблонах; функция `page()` из ПР5 удалена.

Общая структура сайта задана в `templates/base.html`. Дочерние шаблоны
наследуют его через `{% extends %}` и переопределяют блоки `title` и `content`.
Навигация вынесена в `templates/includes/navigation.html`; карточки идей,
карточки категорий и статусы подключаются через `{% include %}`.

Коллекции выводятся с помощью `{% for %}`, пустые списки обрабатываются
веткой `{% empty %}`, доступность идеи и активный пункт навигации определяются
через `{% if %}`. Данные экранируются средствами Django автоматически.

Все внутренние ссылки используют `{% url %}`. Приложения имеют пространства
имён: `homepage`, `catalog`, `taxonomy`. Адреса страниц сохранены:

| Страница | URL | Имя маршрута |
| --- | --- | --- |
| Главная | `/` | `homepage:index` |
| Каталог идей | `/ideas/` | `catalog:ideas` |
| Подробности идеи | `/ideas/<id>/` | `catalog:idea_detail` |
| Категории | `/categories/` | `taxonomy:categories` |
| Идеи категории | `/categories/<id>/` | `taxonomy:category_detail` |

Для неизвестных объектов возвращается ответ 404 с шаблоном приложения.
Для неизвестных маршрутов при `DEBUG=False` используется общий `templates/404.html`.

Фильтры используются на данных проекта: `length` показывает количество
элементов, `default` подставляет отсутствующие названия и сведения об авторе,
`truncatechars` сокращает описание карточки, `date` форматирует дату создания,
`linebreaksbr` сохраняет переносы строк в полном описании.

Статические ресурсы подключаются через `{% load static %}` и `{% static %}`:

- `static/css/site.css` оформляет страницы, карточки и статусы;
- `homepage/static/homepage/img/logo.svg` содержит логотип сайта;
- `homepage/static/homepage/js/main.js` обновляет год в подвале.

```text
templates/
├── base.html
├── 404.html
└── includes/navigation.html
homepage/
├── templates/homepage/index.html
└── static/homepage/
    ├── img/logo.svg
    └── js/main.js
catalog/templates/catalog/
├── idea_list.html
├── idea_detail.html
├── idea_not_found.html
└── includes/
    ├── idea_card.html
    └── idea_status.html
taxonomy/templates/taxonomy/
├── category_list.html
├── category_detail.html
├── category_not_found.html
└── includes/category_card.html
static/css/site.css
```

Данные предметной области остаются в `data/ideas.json`, `data/categories.json`
и `data/users.json`. Используются существующие классы `Idea`, `Category`, `User`
и `Status`, модули хранения и консольная версия ПР3. Веб-формы ещё не реализованы.
Django ORM для предметной области ещё не используется; переход к базе данных
относится к следующим практическим работам.

### Запуск и проверки

```bash
python -m pip install -r requirements.txt
python manage.py runserver
python manage.py check
pytest -v
flake8 . --extend-exclude=venv
mypy .
python manage.py findstatic css/site.css homepage/img/logo.svg homepage/js/main.js
```

При проверке ПР6 успешно прошли 32 теста, проверки Django, flake8 и mypy.

### Дальнейшее развитие

Следующий этап: перенос данных предметной области из JSON в базу данных
через Django ORM и реализация веб-форм. Переход на Django-шаблоны выполнен в ПР6.
