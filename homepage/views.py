from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from web_data import load_project_data
from web_page import page


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    content = f"""
<h1 class="text-danger">404 – страница не найдена</h1>
<p>Проверьте адрес или вернитесь на главную.</p>
<a href="{reverse('index')}" class="btn btn-primary">На главную</a>
"""
    return HttpResponse(page("404 – страница не найдена", content), status=404)


def index(request: HttpRequest) -> HttpResponse:
    data = load_project_data()
    available = sum(idea.is_available for idea in data.ideas)
    content = f"""
<section class="hero mb-4">
  <div class="hero-copy">
    <span class="eyebrow">Место, где начинаются проекты</span>
    <h1>Большие проекты<br>начинаются с <span>идеи.</span></h1>
    <p class="lead">Найдите тему, которую захочется воплотить.
      Выбирайте язык, изучайте идеи и делайте первый шаг к своему проекту.</p>
    <div class="d-flex gap-2 flex-wrap mt-4">
      <a class="btn btn-primary btn-lg" href="{reverse('ideas')}">Найти идею →</a>
      <a class="btn btn-outline-primary btn-lg" href="{reverse('categories')}">Выбрать язык</a>
    </div>
    <p class="hero-note">Для учёбы, практики и вашего следующего pet-проекта</p>
  </div>
  <div class="hero-art" aria-hidden="true">
    <div class="art-orbit"></div>
    <div class="code-window">
      <div class="code-toolbar"><span></span><span></span><span></span><b>next_project.py</b></div>
      <div class="code-content">
        <div><span class="code-comment"># всё начинается здесь</span></div>
        <div><span class="code-key">idea</span> = <span class="code-string">"Что-то классное"</span></div>
        <div><span class="code-key">skills</span> = [<span class="code-string">"любопытство"</span>]</div>
        <div class="code-gap"><span class="code-comment"># следующий шаг — за вами</span></div>
        <div><span class="code-call">build</span>(idea, skills)</div>
        <div class="code-result">→ Ваш следующий проект</div>
      </div>
    </div>
    <div class="art-label">✦ Одна идея. Много возможностей.</div>
  </div>
</section>
<div class="section-heading"><span class="eyebrow">Всё для первого шага</span>
  <span class="text-muted small">Исследуйте каталог в своём темпе</span></div>
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
    return HttpResponse(page("Главная", content, active="home"))
