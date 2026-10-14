-- IdeaHub PR7. Named sections are executed directly by the application.
-- User values are bound to ? placeholders; never interpolated into SQL.

-- name: categories
-- 1. List categories (SELECT, ORDER BY); /ideas/ and /.
SELECT id, name FROM categories ORDER BY name, id;

-- name: users
-- 2. List public author names (SELECT, ORDER BY); catalog search form.
SELECT id, name FROM users ORDER BY name, id;

-- name: ideas
-- 3. Catalog with linked category, author and selector (JOIN, LIMIT, OFFSET). Parameters: limit, offset.
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
-- 4. Linked idea details (JOIN, WHERE). Parameter: idea id.
SELECT i.id, i.title, i.description, i.category_id, i.author_id, i.status,
       i.selected_by_id, i.created_at, (i.status = 'не взята') AS is_available,
       c.name AS category_name, a.name AS author_name, s.name AS selected_by_name
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE i.id = ?;

-- name: filtered_ideas
-- 5. Search by literal title fragment, language, author and status (WHERE). Parameters: q twice, category twice, author twice, status twice, sort twice, limit, offset.
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
-- 6. Available projects by title fragment and language (WHERE). Parameters: q twice, category twice.
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
-- 7. Selected projects with user names (JOIN, WHERE); /ideas/selected/.
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
-- 8. A category by id (WHERE). Parameter: category id.
SELECT id, name FROM categories WHERE id = ?;

-- name: category_ideas
-- 9. Projects belonging to a category (JOIN, WHERE). Parameter: category id.
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
-- 10. Total/available/selected counts and earliest/latest creation dates (COUNT, SUM, MIN, MAX); homepage and statistics.
SELECT COUNT(*) AS total,
       COALESCE(SUM(status = 'не взята'), 0) AS available,
       COALESCE(SUM(status = 'взята'), 0) AS taken,
       MIN(created_at) AS first_created, MAX(created_at) AS last_created
FROM ideas;

-- name: user_totals
-- 11. Number of contributors and users with a selected idea (aggregates); statistics.
SELECT COUNT(DISTINCT author_id) AS authors,
       COUNT(DISTINCT selected_by_id) AS selectors
FROM ideas;

-- name: category_statistics
-- 12. Projects by category including categories with no projects (LEFT JOIN, GROUP BY, COUNT); categories and statistics.
SELECT c.id, c.name, COUNT(i.id) AS count,
       COALESCE(SUM(i.status = 'не взята'), 0) AS available,
       COALESCE(SUM(i.status = 'взята'), 0) AS taken
FROM categories AS c
LEFT JOIN ideas AS i ON i.category_id = c.id
GROUP BY c.id, c.name
ORDER BY count DESC, c.name, c.id;

-- name: author_statistics
-- 13. Authors and their project counts including users with no ideas (LEFT JOIN, GROUP BY, COUNT); /ideas/authors/ and statistics.
SELECT u.id, u.name, COUNT(i.id) AS count,
       COALESCE(SUM(i.status = 'не взята'), 0) AS available
FROM users AS u
LEFT JOIN ideas AS i ON i.author_id = u.id
GROUP BY u.id, u.name
ORDER BY count DESC, u.name, u.id;

-- name: popular_categories
-- 14. Categories meeting the minimum number of projects (GROUP BY, HAVING). Parameter: minimum count; statistics form.
SELECT c.id, c.name, COUNT(i.id) AS count
FROM categories AS c
LEFT JOIN ideas AS i ON i.category_id = c.id
GROUP BY c.id, c.name
HAVING COUNT(i.id) >= ?
ORDER BY count DESC, c.name, c.id;

-- name: status_statistics
-- 15. Distribution of projects by status (GROUP BY, COUNT); statistics.
SELECT status, COUNT(*) AS count
FROM ideas
GROUP BY status
ORDER BY status;

-- name: recent_ideas
-- 16. Most recently created projects (ORDER BY, LIMIT). Parameter: limit; homepage.
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
-- 17. Count matching projects for pagination (COUNT, WHERE). Parameters: q twice, category twice, author twice, status twice.
SELECT COUNT(*) AS count
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
JOIN users AS a ON a.id = i.author_id
LEFT JOIN users AS s ON s.id = i.selected_by_id
WHERE (? = '' OR instr(i.title, ?) > 0)
  AND (? IS NULL OR i.category_id = ?)
  AND (? IS NULL OR i.author_id = ?)
  AND (? = '' OR i.status = ?);
