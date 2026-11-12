from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from catalog.models import Idea
from participants.models import User
from passwords import hash_password


def sign_in(client, participant_id):
    participant = User.objects.get(pk=participant_id)
    participant.password = hash_password("test-password")
    participant.save(update_fields=["password"])
    url = reverse("participants:login")
    client.get(url)
    response = client.post(url, {
        "name": participant.name,
        "password": "test-password",
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    })
    assert response.status_code == 302


def picture(name="idea.png", color="white"):
    stream = BytesIO()
    Image.new("RGB", (16, 12), color).save(stream, "PNG")
    return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")


def test_bound_filter_shows_errors_and_keeps_other_values(client):
    response = client.get(reverse("catalog:ideas"), {"q": "Трекер", "created_at": "2026-02-30"})
    assert response.status_code == 400
    assert response.context["form"]["created_at"].errors
    assert 'value="Трекер"' in response.content.decode()


def test_create_edit_and_display_image(tmp_path):
    client = Client(enforce_csrf_checks=True)
    create_url = reverse("catalog:idea_create")
    assert client.get(create_url).url == reverse("participants:login")
    sign_in(client, 2)

    assert 'enctype="multipart/form-data"' in client.get(create_url).content.decode()
    data = {
        "title": "Новая идея", "description": "Описание проекта", "category": 1,
        "author": 3, "selected_by": 3, "status": Idea.Status.TAKEN, "created_at": "2020-01-01",
    }
    assert client.post(create_url, data).status_code == 403
    data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value

    with override_settings(MEDIA_ROOT=tmp_path):
        invalid = client.post(create_url, {
            **data, "description": "   ",
            "image": SimpleUploadedFile("bad.png", b"broken", content_type="image/png"),
        })
        assert set(invalid.context["form"].errors) == {"description", "image"}
        assert not Idea.objects.filter(title=data["title"]).exists()

        created = client.post(create_url, {**data, "image": picture()})
        idea = Idea.objects.get(title=data["title"])
        assert created.url == idea.get_absolute_url()
        assert idea.created_at == timezone.localdate()
        assert idea.is_available and idea.selected_by_id is None and idea.author_id == 2
        assert (tmp_path / idea.image.name).is_file()
        assert idea.image.url in client.get(created.url).content.decode()

        edit_url = reverse("catalog:idea_edit", args=[idea.pk])
        assert client.get(edit_url).status_code == 403
        sign_in(client, 1)
        assert client.get(edit_url).context["form"].initial["title"] == idea.title
        assert client.get(reverse("catalog:idea_edit", args=[99999])).status_code == 404
        count = Idea.objects.count()
        response = client.post(edit_url, {
            **data, "title": "Обновлённая идея", "image": picture("replacement.png", "black"),
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        assert response.url == idea.get_absolute_url()
        idea.refresh_from_db()
        assert idea.title == "Обновлённая идея" and idea.author_id == 2
        assert idea.image.name == "ideas/replacement.png"
        assert Idea.objects.count() == count


def test_selection_conflict_and_release_preserve_idea():
    first = Client(enforce_csrf_checks=True)
    second = Client(enforce_csrf_checks=True)
    sign_in(first, 2)
    sign_in(second, 4)
    select = reverse("catalog:idea_select", args=[1])
    release = reverse("catalog:idea_release", args=[1])
    first_token = {"csrfmiddlewaretoken": first.cookies["csrftoken"].value}
    second_token = {"csrfmiddlewaretoken": second.cookies["csrftoken"].value}

    assert first.get(select).status_code == first.get(release).status_code == 405
    assert first.post(select).status_code == first.post(release).status_code == 403
    assert first.post(select, first_token).status_code == 302
    assert second.post(select, second_token).context["selection_form"].non_field_errors()
    another = reverse("catalog:idea_select", args=[3])
    assert first.post(another, first_token).context["selection_form"].non_field_errors()
    assert second.post(release, second_token).status_code == 403
    assert Idea.objects.taken().get(pk=1).selected_by_id == 2
    assert first.post(release, first_token).status_code == 302
    assert Idea.objects.available().get(pk=1).selected_by_id is None
    assert second.post(select, second_token).status_code == 302
    assert Idea.objects.taken().get(pk=1).selected_by_id == 4


def test_admin_can_upload_and_replace_image(client, tmp_path):
    client.force_login(get_user_model().objects.create_superuser(username="admin", password="test-password"))
    idea = Idea.objects.get(pk=2)
    url = reverse("admin:catalog_idea_change", args=[idea.pk])
    data = {
        "title": idea.title, "description": idea.description, "category": idea.category_id,
        "author": idea.author_id, "status": idea.status, "selected_by": idea.selected_by_id,
        "created_at": idea.created_at.isoformat(),
    }
    with override_settings(MEDIA_ROOT=tmp_path):
        for name in ("first.png", "second.png"):
            response = client.post(url, {**data, "image": picture(name)})
            assert response.status_code == 302
            idea.refresh_from_db()
            assert idea.image.name == f"ideas/{name}"
            assert (tmp_path / idea.image.name).is_file()
            assert idea.image.url in client.get(idea.get_absolute_url()).content.decode()
