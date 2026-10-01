"""Главная страница IdeaHub."""
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from web_data import load_project_data
from web_page import page


def index(request: HttpRequest) -> HttpResponse:
    data = load_project_data()
    available = sum(idea.is_available for idea in data.ideas)
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
    <div class="stat-number">{len(data.ideas)}</div><div>идей в каталоге</div>
  </div></div>
  <div class="col-sm-4"><div class="stat-card p-4 rounded-4 h-100">
    <div class="stat-number">{available}</div><div>свободных идей</div>
  </div></div>
  <div class="col-sm-4"><div class="stat-card p-4 rounded-4 h-100">
    <div class="stat-number">{len(data.categories)}</div><div>категорий</div>
  </div></div>
</div>"""
    return HttpResponse(page("Главная", content))
