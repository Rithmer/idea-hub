from datetime import date

ideas = []


categories = [
    "Социальные инициативы",
    "Продуктивность",
    "Финансы",
    "Образование",
    "Экология",
    "Транспорт",
]


def add_category(name):
    name = name.strip()

    if not name:
        print("Название категории не может быть пустым.")
        return None

    for existing in categories:
        if existing.lower() == name.lower():
            print("Такая категория уже существует.")
            return None

    categories.append(name)
    print(f"Категория «{name}» добавлена.")
    return name


def print_categories():
    if not categories:
        print("Список категорий пуст.")
        return

    for i, cat in enumerate(categories, start=1):
        print(f"{i}. {cat}")


def choose_category():
    print_categories()

    choice = input(
        "Введите номер категории (или новое название): "
    ).strip()

    if choice.isdigit():
        index = int(choice) - 1

        if 0 <= index < len(categories):
            return categories[index]

        print("Неверный номер, категория не выбрана.")
        return None

    return add_category(choice)


def normalize_query(query):
    return str(query).strip().lower()


def add_idea(
    title,
    description,
    category,
    author,
    status="не взята",
    created_at=None
):
    if created_at is None:
        created_at = date.today()

    if status not in ("не взята", "взята"):
        raise ValueError(
            'Статус должен быть "не взята" или "взята"'
        )

    idea = {
        "title": title,
        "description": description,
        "category": category,
        "author": author,
        "status": status,
        "created_at": created_at,
    }

    ideas.append(idea)
    return idea


def take_idea(title):
    for idea in ideas:
        if idea["title"].lower() == title.lower():
            idea["status"] = "взята"
            return idea

    return None


def release_idea(title):
    for idea in ideas:
        if idea["title"].lower() == title.lower():
            idea["status"] = "не взята"
            return idea

    return None


def idea_matches_query(query, idea):
    prepared_query = normalize_query(query)

    if not prepared_query:
        return False

    return (
        prepared_query in idea["title"].lower()
        or prepared_query in idea["category"].lower()
    )


def search_ideas(query):
    return [
        idea
        for idea in ideas
        if idea_matches_query(query, idea)
    ]


def get_status_message(status):
    if status == "взята":
        return "Идея уже взята в работу."

    if status == "не взята":
        return "Идея пока свободна и ждёт своего автора."

    return "Статус идеи требует уточнения."


def print_idea_short(idea):
    print(f"Название: {idea['title']}")
    print(f"Описание: {idea['description']}")


def print_idea_detailed(idea):
    print("=" * 50)
    print(f"Название: {idea['title']}")
    print(f"Описание: {idea['description']}")
    print(f"Категория: {idea['category']}")
    print(f"Автор: {idea['author']}")
    print(f"Дата создания: {idea['created_at']}")
    print(
        f"Статус: {idea['status']} — "
        f"{get_status_message(idea['status'])}"
    )
    print("=" * 50)


def print_search_results(query):
    results = search_ideas(query)

    if not results:
        print("По вашему запросу подходящая идея не найдена.")
        return

    print(f"Найдено идей: {len(results)}\n")

    for idea in results:
        print_idea_short(idea)
        print("-" * 30)


def print_detailed_search_results(query):
    results = search_ideas(query)

    if not results:
        print("По вашему запросу подходящая идея не найдена.")
        return

    print(f"Найдено идей: {len(results)}\n")

    for idea in results:
        print_idea_detailed(idea)


def view_idea_details(title):
    for idea in ideas:
        if idea["title"].lower() == title.lower():
            print_idea_detailed(idea)
            return idea

    print("Идея с таким названием не найдена.")
    return None


def seed_ideas():

    add_idea(
        title="Приложение для поиска волонтёрских проектов",
        description=(
            "Сервис, который помогает находить волонтёрские "
            "инициативы рядом с пользователем."
        ),
        category="Социальные инициативы",
        author="Анна Смирнова",
        status="не взята",
        created_at=date(2026, 9, 9),
    )

    add_idea(
        title="Трекер привычек с геймификацией",
        description=(
            "Приложение для отслеживания привычек "
            "с очками и уровнями."
        ),
        category="Продуктивность",
        author="Иван Петров",
        status="взята",
        created_at=date(2026, 9, 5),
    )

    add_idea(
        title="Платформа для обмена книгами",
        description=(
            "Сервис, позволяющий соседям "
            "обмениваться книгами бесплатно."
        ),
        category="Социальные инициативы",
        author="Мария Кузнецова",
        status="не взята",
        created_at=date(2026, 8, 28),
    )

    add_idea(
        title="Трекер расходов для студентов",
        description=(
            "Простое приложение для учёта расходов "
            "и планирования стипендии."
        ),
        category="Финансы",
        author="Дмитрий Соколов",
        status="не взята",
        created_at=date(2026, 9, 1),
    )

    add_idea(
        title="Онлайн-платформа для менторства",
        description=(
            "Сервис для поиска ментора в IT-сфере "
            "и записи на консультации."
        ),
        category="Образование",
        author="Ольга Волкова",
        status="взята",
        created_at=date(2026, 8, 20),
    )

    add_idea(
        title="Экоприложение для сортировки мусора",
        description=(
            "Приложение подсказывает, куда сдать разные "
            "виды отходов рядом с домом."
        ),
        category="Экология",
        author="Сергей Морозов",
        status="не взята",
        created_at=date(2026, 9, 3),
    )

    add_idea(
        title="Трекер тренировок дома",
        description=(
            "Приложение с готовыми программами "
            "тренировок без спортзала."
        ),
        category="Продуктивность",
        author="Екатерина Новикова",
        status="не взята",
        created_at=date(2026, 9, 7),
    )

    add_idea(
        title="Сервис поиска попутчиков для поездок",
        description=(
            "Платформа для совместных поездок "
            "на дальние расстояния."
        ),
        category="Транспорт",
        author="Алексей Фёдоров",
        status="взята",
        created_at=date(2026, 8, 15),
    )


def print_menu():
    print("\n===== Меню =====")
    print("1. Поиск идей")
    print("2. Подробный поиск идей")
    print("3. Добавить идею")
    print("4. Изменить статус идеи (взята / не взята)")
    print("5. Добавить категорию")
    print("0. Выход")


def handle_search():
    query = input("Введите запрос для поиска идеи: ")
    print_search_results(query)


def handle_detailed_search():
    query = input("Введите запрос для подробного поиска идеи: ")
    print_detailed_search_results(query)


def handle_add_idea():
    title = input("Название идеи: ").strip()

    if not title:
        print("Название не может быть пустым.")
        return

    description = input("Описание идеи: ").strip()
    author = input("Автор: ").strip()

    category = choose_category()

    if category is None:
        print("Идея не добавлена: категория не выбрана.")
        return

    add_idea(
        title=title,
        description=description,
        category=category,
        author=author,
        status="не взята",
    )

    print(
        f"Идея «{title}» добавлена "
        f"в категорию «{category}»."
    )


def handle_change_status():
    title = input(
        "Введите точное название идеи: "
    ).strip()

    idea = None

    for existing in ideas:
        if existing["title"].lower() == title.lower():
            idea = existing
            break

    if idea is None:
        print("Идея с таким названием не найдена.")
        return

    print(f"Текущий статус: {idea['status']}")
    print("1. Взята")
    print("2. Не взята")

    choice = input("Выберите новый статус: ").strip()

    if choice == "1":
        take_idea(title)
        print(
            f"Статус идеи «{title}» "
            f"изменён на «взята»."
        )

    elif choice == "2":
        release_idea(title)
        print(
            f"Статус идеи «{title}» "
            f"изменён на «не взята»."
        )

    else:
        print("Неверный выбор, статус не изменён.")


def handle_add_category():
    name = input(
        "Введите название новой категории: "
    )

    add_category(name)


def run_menu():
    actions = {
        "1": handle_search,
        "2": handle_detailed_search,
        "3": handle_add_idea,
        "4": handle_change_status,
        "5": handle_add_category,
    }

    while True:
        print_menu()

        choice = input(
            "Выберите действие: "
        ).strip()

        if choice == "0":
            print("Выход из программы.")
            break

        action = actions.get(choice)

        if action is None:
            print(
                "Неверный пункт меню, попробуйте снова."
            )
            continue

        action()


if __name__ == "__main__":
    seed_ideas()
    run_menu()