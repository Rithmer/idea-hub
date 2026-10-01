"""Общий HTML-каркас веб-страниц ПР5."""
from html import escape

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def page(title: str, content: str) -> str:
    """Собрать HTML-документ с навигацией и общими стилями."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
        "dist/css/bootstrap.min.css"
    )
    css_url = staticfiles_storage.url("css/site.css")
    home_url = reverse("index")
    ideas_url = reverse("ideas")
    categories_url = reverse("categories")
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · IdeaHub</title>
  <link rel="stylesheet" href="{bootstrap}">
  <link rel="stylesheet" href="{css_url}">
</head>
<body>
  <header class="site-header border-bottom">
    <nav class="container navbar navbar-expand-sm" aria-label="Основная навигация">
      <a class="navbar-brand fw-bold" href="{home_url}">IdeaHub</a>
      <div class="nav ms-auto">
        <a class="nav-link" href="{home_url}">Главная</a>
        <a class="nav-link" href="{ideas_url}">Идеи</a>
        <a class="nav-link" href="{categories_url}">Категории</a>
      </div>
    </nav>
  </header>
  <main class="container py-5">{content}</main>
  <footer class="container border-top py-3 text-muted small">
    IdeaHub · каталог проектных идей
  </footer>
</body>
</html>"""
