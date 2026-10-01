from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from categories import get_category_by_id
from web_data import load_project_data
from web_page import page


def categories(request: HttpRequest) -> HttpResponse:
    data = load_project_data()
    ideas = data.ideas
    categories_list = data.categories
    cards = []
    for category in categories_list:
        count = sum(idea.category_id == category.id for idea in ideas)
        url = reverse("category_detail", args=[category.id])
        cards.append(f"""
<div class="col-sm-6 col-lg-4"><div class="card h-100 shadow-sm idea-card">
  <div class="card-body p-4">
    <h2 class="h4"><a class="stretched-link" href="{url}">
      {escape(category.name)}</a></h2>
    <p class="text-muted mb-0">Идей: {count}</p>
  </div>
</div></div>""")
    listing = ("<div class=\"row g-4\">" + "".join(cards) + "</div>"
               if cards else "<p>Пока нет категорий.</p>")
    content = f"""
<span class="eyebrow">Направления</span>
<h1 class="display-6 fw-bold mb-4">Категории</h1>
{listing}"""
    return HttpResponse(page("Категории", content))


def category_detail(request: HttpRequest, category_id: int) -> HttpResponse:
    data = load_project_data()
    ideas = data.ideas
    categories_list = data.categories
    category = get_category_by_id(categories_list, category_id)
    if category is None:
        content = ("<h1>Категория не найдена</h1>"
                   f'<a href="{reverse("categories")}">К категориям</a>')
        return HttpResponse(page("Категория не найдена", content), status=404)
    items = []
    for idea in ideas:
        if idea.category_id == category_id:
            url = reverse("idea_detail", args=[idea.id])
            label = "Свободна" if idea.is_available else "Взята"
            items.append(f'<li class="list-group-item">'
                         f'<a href="{url}">{escape(idea.title)}</a>'
                         f'<span class="float-end text-muted">{label}</span></li>')
    listing = ("<ul class=\"list-group\">" + "".join(items) + "</ul>"
               if items else "<p>В этой категории пока нет идей.</p>")
    content = f"""
<a class="back-link" href="{reverse('categories')}">← К категориям</a>
<h1 class="display-6 fw-bold mt-4">{escape(category.name)}</h1>
<p class="text-muted mb-4">Идеи на этом языке программирования</p>
{listing}"""
    return HttpResponse(page(category.name, content))
