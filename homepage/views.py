"""Главная страница и общий каркас HTML для ПР5."""
from html import escape

from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
from django.urls import reverse

from web_data import load_project_data


def page(title: str, content: str) -> str:
    """Собрать единую страницу; шаблоны появятся на следующем этапе."""
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


def index(request):
    ideas, categories, _ = load_project_data()
    available = sum(idea.is_available for idea in ideas)
    content = f"""
<section class="hero p-4 p-md-5 rounded-4 mb-5">
  <span class="eyebrow">Найдите тему для следующего проекта</span>
  <h1 class="display-5 fw-bold mt-3">Идея для вашего проекта уже здесь</h1>
  <p class="lead col-lg-8">Просматривайте идеи по языкам программирования,
    узнавайте подробности и проверяйте, свободна ли тема.</p>
  <div class="d-flex gap-2 flex-wrap mt-4">
    <a class="btn btn-primary btn-lg" href="{reverse('ideas')}">Смотреть идеи</a>
    <a class="btn btn-outline-primary btn-lg" href="{reverse('categories')}">
      Категории</a>
  </div>
</section>
<div class="row g-3">
  <div class="col-sm-4"><div class="stat-card p-4 rounded-4 h-100">
    <div class="stat-number">{len(ideas)}</div><div>идей в каталоге</div>
  </div></div>
  <div class="col-sm-4"><div class="stat-card p-4 rounded-4 h-100">
    <div class="stat-number">{available}</div><div>свободных идей</div>
  </div></div>
  <div class="col-sm-4"><div class="stat-card p-4 rounded-4 h-100">
    <div class="stat-number">{len(categories)}</div><div>категорий</div>
  </div></div>
</div>"""
    return HttpResponse(page("Главная", content))
