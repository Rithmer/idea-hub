"""Проверки администрирования и ORM-сценариев ПР10."""
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from catalog.models import Idea
from participants.models import User
from passwords import verify_password
from taxonomy.models import Category


def test_admin_lists_related_ideas(client):
    client.force_login(get_user_model().objects.create_superuser(username="pr10"))
    response = client.get(reverse("admin:catalog_idea_changelist"), {
        "q": "Иван Петров", "status__exact": Idea.Status.TAKEN,
    })
    assert response.status_code == 200
    assert [idea.pk for idea in response.context["cl"].result_list] == [2]

    for admin_view, pk, links in (
        ("admin:taxonomy_category_change", 3, {2}),
        ("admin:participants_user_change", 3, {2}),
    ):
        response = client.get(reverse(admin_view, args=[pk]))
        assert response.status_code == 200
        inline_ids = {
            idea.pk for inline in response.context["inline_admin_formsets"]
            for idea in inline.formset.get_queryset()
        }
        assert inline_ids == links

    idea = Idea.objects.get(pk=2)
    assert client.get(idea.get_absolute_url()).status_code == 200
    assert client.get(Category.objects.get(pk=3).get_absolute_url()).status_code == 200


def test_admin_status_change_updates_availability_and_statistics(client):
    client.force_login(get_user_model().objects.create_superuser(username="pr10"))
    idea = Idea.objects.get(pk=2)
    form = {
        "title": idea.title, "description": idea.description,
        "category": idea.category_id, "author": idea.author_id,
        "created_at": idea.created_at.isoformat(), "status": Idea.Status.AVAILABLE,
        "selected_by": idea.selected_by_id,
    }
    url = reverse("admin:catalog_idea_change", args=[idea.pk])
    invalid = client.post(url, form)
    assert invalid.context["adminform"].form.non_field_errors()
    idea.refresh_from_db()
    assert idea.status == Idea.Status.TAKEN

    form["selected_by"] = ""
    assert client.post(url, form).status_code == 302
    assert idea.pk in [row.pk for row in client.get(reverse("catalog:available")).context["ideas"]]
    assert client.get(reverse("catalog:statistics")).context["totals"]["taken"] == 0


def participant_form_data(client, url, **fields):
    response = client.get(url)
    for inline in response.context["inline_admin_formsets"]:
        management = inline.formset.management_form
        fields.update({management.add_prefix(name): value for name, value in management.initial.items()})
    return fields


def test_admin_participant_password_is_hashed_and_preserved(client):
    client.force_login(get_user_model().objects.create_superuser(username="pr10"))
    add_url = reverse("admin:participants_user_add")
    form = participant_form_data(client, add_url, name="Новый участник", new_password="example-password")
    assert client.post(add_url, form).status_code == 302
    user = User.objects.get(name="Новый участник")
    password_hash = user.password
    assert password_hash.startswith("pbkdf2_sha256$")
    assert verify_password(password_hash, "example-password")

    url = reverse("admin:participants_user_change", args=[user.pk])
    assert password_hash not in client.get(url).content.decode()
    form = participant_form_data(client, url, name="Переименованный участник")
    assert client.post(url, form).status_code == 302
    user.refresh_from_db()
    assert user.password == password_hash


def test_creation_date_filter_and_pagination_do_not_cause_n_plus_one(client):
    Idea.objects.bulk_create([
        Idea(title=f"Демо {number:02}", description="ПР10",
             category_id=1, author_id=2, created_at="2026-09-09")
        for number in range(13)
    ])
    url = reverse("catalog:ideas")
    filters = {
        "created_at": "2026-09-09", "category": 1, "author": 2,
        "sort": "title", "status": Idea.Status.AVAILABLE,
    }
    with CaptureQueriesContext(connection) as listing:
        response = client.get(url, filters)
    assert len(listing) == 4
    assert response.context["total"] == 14
    assert "created_at=2026-09-09" in response.content.decode()
    assert "page=2" in response.content.decode()
    assert client.get(url, {**filters, "page": 2}).context["page_obj"].number == 2
    assert client.get(url, {"created_at": "2026-02-30"}).status_code == 400

    with CaptureQueriesContext(connection) as detail:
        assert client.get(reverse("catalog:idea_detail", args=[2])).status_code == 200
    assert len(detail) == 1
    assert "JOIN" in detail[0]["sql"]
