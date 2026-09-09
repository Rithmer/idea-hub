from datetime import date


def normalize_query(query):
    return str(query).strip().lower()


def idea_matches_query(query, title, category):
    prepared_query = normalize_query(query)
    if not prepared_query:
        return False
    return prepared_query in title.lower() or prepared_query in category.lower()


def get_status_message(status):
    if status == "published":
        return "Идея опубликована и доступна для просмотра."
    if status == "draft":
        return "Идея пока сохранена как черновик."
    return "Статус идеи требует уточнения."


def print_search_result(query, title, category, author, status, created_at):
    if idea_matches_query(query, title, category):
        print("Идея найдена:")
        print(f"Название: {title}")
        print(f"Категория: {category}")
        print(f"Автор: {author}")
        print(f"Дата создания: {created_at}")
        print(get_status_message(status))
    else:
        print("По вашему запросу подходящая идея не найдена.")


idea_title = "Приложение для поиска волонтёрских проектов"
idea_category = "Социальные инициативы"
idea_author = "Анна Смирнова"
idea_status = "published"
idea_created_at = date(2026, 9, 9)

user_query = input("Введите запрос для поиска идеи: ")
print_search_result(
    user_query,
    idea_title,
    idea_category,
    idea_author,
    idea_status,
    idea_created_at,
)
