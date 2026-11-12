"""Представления каталога, проверка параметров и постраничный вывод."""
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from catalog import queries
from catalog.forms import AvailableIdeaFilterForm, IdeaFilterForm, IdeaForm, SelectIdeaForm
from catalog.models import Idea
from catalog.parameters import integer_parameter
from participants.models import User
from participants.views import current_participant


PAGE_SIZE = 12


def invalid_search(request: HttpRequest, message: str) -> HttpResponse:
    """Возвращает страницу с пояснением ошибки ввода и HTTP-статусом 400."""
    return render(request, "catalog/invalid_search.html", {"message": message}, status=400)


def ideas(request: HttpRequest) -> HttpResponse:
    """Показывает каталог с фильтрами, сортировкой и сохранением параметров пагинации."""
    form = IdeaFilterForm(request.GET)
    if not form.is_valid():
        return render(request, "catalog/idea_list.html", {"form": form}, status=400)
    filters = form.cleaned_data
    sort = filters["sort"]
    listing = queries.filtered_ideas(
        q=filters["q"], category=filters["category"], author=filters["author"],
        status=filters["status"], created_at=filters["created_at"],
    ).order_by(*queries.SORT_ORDERS[sort])
    paginator = Paginator(listing, PAGE_SIZE)
    try:
        page = paginator.page(request.GET.get("page") or 1)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        return render(request, "404.html", status=404)
    context = {
        "form": form, "ideas": page.object_list, "page_obj": page, "total": paginator.count,
        "is_filtered": any(filters[field] for field in ("q", "category", "author", "status", "created_at")),
    }
    return render(request, "catalog/idea_list.html", context)


def idea_detail(request: HttpRequest, idea_id: int) -> HttpResponse:
    """Показывает идею со связанными объектами или возвращает страницу 404."""
    try:
        idea = get_object_or_404(queries.idea_listing(), pk=idea_id)
    except Http404:
        return render(request, "catalog/idea_not_found.html", status=404)
    return render_idea_detail(request, idea, current_participant(request))


def render_idea_detail(request: HttpRequest, idea: Idea, participant: User | None,
                       selection_form: SelectIdeaForm | None = None) -> HttpResponse:
    return render(request, "catalog/idea_detail.html", {
        "idea": idea, "created_at": idea.created_at, "participant": participant,
        "selection_form": selection_form,
        "can_release": participant and (participant.is_admin or idea.selected_by_id == participant.pk),
    })


@require_http_methods(["GET", "POST"])
def idea_create(request: HttpRequest) -> HttpResponse:
    participant = current_participant(request)
    if participant is None:
        return redirect("participants:login")
    form = IdeaForm(request.POST, request.FILES) if request.method == "POST" else IdeaForm()
    if form.is_bound and form.is_valid():
        form.instance.author = participant
        return redirect(form.save())
    return render(request, "catalog/idea_form.html", {"form": form, "heading": "Предложить идею"})


@require_http_methods(["GET", "POST"])
def idea_edit(request: HttpRequest, idea_id: int) -> HttpResponse:
    idea = get_object_or_404(Idea, pk=idea_id)
    participant = current_participant(request)
    if participant is None:
        return redirect("participants:login")
    if not participant.is_admin:
        raise PermissionDenied
    data = request.POST if request.method == "POST" else None
    files = request.FILES if request.method == "POST" else None
    form = IdeaForm(data, files, instance=idea)
    if form.is_bound and form.is_valid():
        idea = form.save(commit=False)
        if form.changed_data:
            idea.save(update_fields=form.changed_data)
        return redirect(idea)
    return render(request, "catalog/idea_form.html", {
        "form": form, "idea": idea, "heading": "Редактировать идею",
    })


@require_POST
def idea_select(request: HttpRequest, idea_id: int) -> HttpResponse:
    idea = get_object_or_404(queries.idea_listing(), pk=idea_id)
    participant = current_participant(request)
    if participant is None:
        return redirect("participants:login")
    form = SelectIdeaForm(request.POST, idea=idea, participant=participant)
    if form.is_valid():
        try:
            with transaction.atomic():
                selected = Idea.objects.available().filter(pk=idea_id).update(
                    status=Idea.Status.TAKEN, selected_by=participant,
                )
        except IntegrityError:
            form.add_error(None, "Вы уже выбрали идею. Сначала освободите её.")
        else:
            if selected:
                return redirect(idea)
            form.add_error(None, "Эту идею уже выбрали.")
        idea.refresh_from_db()
    return render_idea_detail(request, idea, participant, form)


@require_POST
def idea_release(request: HttpRequest, idea_id: int) -> HttpResponse:
    idea = get_object_or_404(Idea, pk=idea_id)
    participant = current_participant(request)
    if participant is None:
        return redirect("participants:login")
    if idea.selected_by_id is not None and idea.selected_by_id != participant.pk and not participant.is_admin:
        raise PermissionDenied
    idea.release()
    return redirect(idea)


def available_ideas(request: HttpRequest) -> HttpResponse:
    """Показывает свободные идеи с поиском по названию, описанию и категории."""
    form = AvailableIdeaFilterForm(request.GET)
    if not form.is_valid():
        return render(request, "catalog/available.html", {"form": form}, status=400)
    ideas = queries.available_ideas(form.cleaned_data["q"], form.cleaned_data["category"])
    return render(request, "catalog/available.html", {"form": form, "ideas": ideas})


def selected_ideas(request: HttpRequest) -> HttpResponse:
    """Показывает занятые идеи и выбравших их участников."""
    return render(request, "catalog/selected.html", {"ideas": queries.selected_ideas()})


def authors(request: HttpRequest) -> HttpResponse:
    """Показывает участников и количество опубликованных ими идей."""
    return render(request, "catalog/authors.html", {"authors": queries.author_statistics()})


def statistics(request: HttpRequest) -> HttpResponse:
    """Показывает сводные показатели и категории, прошедшие заданный порог."""
    try:
        minimum = integer_parameter(request.GET, "minimum", 2, minimum=0)
    except ValueError as error:
        return invalid_search(request, str(error))
    context = {
        "totals": queries.idea_totals(),
        "user_totals": queries.user_totals(),
        "category_statistics": queries.category_statistics(),
        "author_statistics": queries.author_statistics(),
        "popular_categories": queries.popular_categories(minimum),
        "status_statistics": queries.status_statistics(),
        "minimum": minimum,
    }
    return render(request, "catalog/statistics.html", context)
