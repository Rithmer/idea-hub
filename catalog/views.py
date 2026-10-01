from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from ideas import get_idea_by_id
from models import Idea
from web_data import load_project_data
from web_page import page


def status_badge(idea: Idea) -> str:
    label = "Свободна" if idea.is_available else "Взята"
    color = "success" if idea.is_available else "secondary"
    return f'<span class="badge text-bg-{color}">{label}</span>'


def ideas(request: HttpRequest) -> HttpResponse:
    idea_list = load_project_data().ideas
    cards = []
    for idea in idea_list:
        url = reverse("idea_detail", args=[idea.id])
        category = escape(idea.category.name if idea.category else "Без категории")
        cards.append(f"""
<article class="col-md-6">
  <div class="card h-100 shadow-sm idea-card">
    <div class="card-body">
      <div class="d-flex justify-content-between gap-2 mb-3">
        <span class="text-muted small">{category}</span>{status_badge(idea)}
      </div>
      <h2 class="h5 card-title"><a class="stretched-link" href="{url}">
        {escape(idea.title)}</a></h2>
      <p class="card-text text-muted">{escape(idea.description)}</p>
    </div>
  </div>
</article>""")
    listing = ("<div class=\"row g-4\">" + "".join(cards) + "</div>"
               if cards else "<p>Пока нет идей.</p>")
    content = f"""
<div class="page-heading mb-4">
  <span class="eyebrow">Каталог</span>
  <h1 class="display-6 fw-bold">Идеи для проектов</h1>
  <p class="text-muted">Выберите тему и откройте карточку, чтобы узнать детали.</p>
</div>
{listing} """
    return HttpResponse(page("Идеи", content))


def idea_detail(request: HttpRequest, idea_id: int) -> HttpResponse:
    idea_list = load_project_data().ideas
    idea = get_idea_by_id(idea_list, idea_id)
    if idea is None:
        content = ("<h1>Идея не найдена</h1>"
                   f'<a href="{reverse("ideas")}">К списку идей</a>')
        return HttpResponse(page("Идея не найдена", content), status=404)
    category = escape(idea.category.name if idea.category else "Без категории")
    author = escape(idea.author.name if idea.author else "Неизвестен")
    selected = (escape(idea.selected_by.name) if idea.selected_by else "—")
    category_url = (reverse("category_detail", args=[idea.category_id])
                    if idea.category else reverse("categories"))
    content = f"""
<a class="back-link" href="{reverse('ideas')}">← К каталогу</a>
<article class="card shadow-sm mt-4 detail-card">
  <div class="card-body p-4 p-md-5">
    <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
      <a href="{category_url}" class="eyebrow">{category}</a>
      {status_badge(idea)}
    </div>
    <h1 class="display-6 fw-bold">{escape(idea.title)}</h1>
    <p class="lead mt-4">{escape(idea.description)}</p>
    <dl class="row border-top pt-4 mt-4 mb-0">
      <dt class="col-sm-4">Автор</dt><dd class="col-sm-8">{author}</dd>
      <dt class="col-sm-4">Дата создания</dt>
      <dd class="col-sm-8">{escape(idea.created_at)}</dd>
      <dt class="col-sm-4">Выбрал</dt><dd class="col-sm-8">{selected}</dd>
    </dl>
  </div>
</article>"""
    return HttpResponse(page(idea.title, content))
