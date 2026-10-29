-- Запросы ПР7: сохранены для проверки предыдущего этапа.
-- Сайт ПР9 получает данные через catalog/queries.py (Django ORM).

-- name: categories
SELECT id, name FROM categories ORDER BY name, id;

-- name: users
SELECT id, name FROM users ORDER BY name, id;

-- name: ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
ORDER BY i.created_at DESC, i.id DESC
LIMIT ? OFFSET ?;

-- name: idea_detail
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE i.id = ?;

-- name: filtered_ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE (? = '' OR instr(i.title, ?) > 0)
  AND (? IS NULL OR i.category_id = ?)
  AND (? IS NULL OR i.author_id = ?)
  AND (? = '' OR i.status = ?)
ORDER BY CASE WHEN ? = 'title' THEN i.title END ASC,
         CASE WHEN ? = 'oldest' THEN i.created_at END ASC,
         i.created_at DESC, i.id DESC
LIMIT ? OFFSET ?;

-- name: available_ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE i.status = 'не взята'
  AND (? = '' OR instr(i.title, ?) > 0)
  AND (? IS NULL OR i.category_id = ?)
ORDER BY i.title, i.id;

-- name: selected_ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE i.status = 'взята'
ORDER BY s.name, i.title, i.id;

-- name: category_detail
SELECT id, name FROM categories WHERE id = ?;

-- name: category_ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE i.category_id = ?
ORDER BY i.title, i.id;

-- name: idea_totals
SELECT COUNT(*) AS total,
       COALESCE(SUM(status = 'не взята'), 0) AS available,
       COALESCE(SUM(status = 'взята'), 0) AS taken,
       MIN(created_at) AS first_created, MAX(created_at) AS last_created
FROM ideas;

-- name: user_totals
SELECT COUNT(DISTINCT author_id) AS authors,
       COUNT(DISTINCT selected_by_id) AS selectors
FROM ideas;

-- name: category_statistics
SELECT c.id, c.name, COUNT(i.id) AS count,
       COALESCE(SUM(i.status = 'не взята'), 0) AS available,
       COALESCE(SUM(i.status = 'взята'), 0) AS taken
FROM categories AS c
LEFT JOIN ideas AS i ON i.category_id = c.id
GROUP BY c.id, c.name
ORDER BY count DESC, c.name, c.id;

-- name: author_statistics
SELECT u.id, u.name, COUNT(i.id) AS count,
       COALESCE(SUM(i.status = 'не взята'), 0) AS available
FROM users AS u
LEFT JOIN ideas AS i ON i.author_id = u.id
GROUP BY u.id, u.name
ORDER BY count DESC, u.name, u.id;

-- name: popular_categories
SELECT c.id, c.name, COUNT(i.id) AS count
FROM categories AS c
LEFT JOIN ideas AS i ON i.category_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(i.id) >= ?
ORDER BY count DESC, c.name, c.id;

-- name: status_statistics
SELECT status, COUNT(*) AS count
FROM ideas
GROUP BY status
ORDER BY status;

-- name: recent_ideas
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
ORDER BY i.created_at DESC, i.id DESC
LIMIT ?;

-- name: filtered_count
SELECT COUNT(*) AS count
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE (? = '' OR instr(i.title, ?) > 0)
  AND (? IS NULL OR i.category_id = ?)
  AND (? IS NULL OR i.author_id = ?)
  AND (? = '' OR i.status = ?);
