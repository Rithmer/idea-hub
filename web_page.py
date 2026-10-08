from html import escape

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def page(title: str, content: str, active: str = "") -> str:
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
        "dist/css/bootstrap.min.css"
    )
    css_url = staticfiles_storage.url("css/site.css")
    home_url = reverse("index")
    ideas_url = reverse("ideas")
    categories_url = reverse("categories")

    def nav_link(url: str, label: str, section: str) -> str:
        current = ' aria-current="page"' if active == section else ""
        return f'<a class="nav-link" href="{url}"{current}>{label}</a>'

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
  <header class="site-header">
    <nav class="container navbar navbar-expand-sm" aria-label="Основная навигация">
      <a class="navbar-brand fw-bold" href="{home_url}">
        <span class="brand-mark" aria-hidden="true">i<span>h</span></span>IdeaHub</a>
      <div class="nav ms-auto">
        {nav_link(home_url, "Главная", "home")}
        {nav_link(ideas_url, "Идеи", "ideas")}
        {nav_link(categories_url, "Категории", "categories")}
      </div>
    </nav>
  </header>
  <main id="main-content" class="container site-main">{content}</main>
  <footer class="container site-footer">
    <span><strong>IdeaHub</strong> · каталог проектных идей</span>
    <span>От первой идеи — к своему проекту.</span>
  </footer>
</body>
</html>"""
