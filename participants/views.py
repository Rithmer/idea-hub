from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import rotate_token
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from participants.forms import ParticipantLoginForm
from participants.models import User


PARTICIPANT_SESSION_KEY = "participant_id"


def current_participant(request: HttpRequest) -> User | None:
    participant_id = request.session.get(PARTICIPANT_SESSION_KEY)
    if participant_id is None:
        return None
    return User.objects.filter(pk=participant_id).first()


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest) -> HttpResponse:
    form = ParticipantLoginForm(request.POST if request.method == "POST" else None)
    if form.is_bound and form.is_valid() and form.participant is not None:
        request.session.cycle_key()
        request.session[PARTICIPANT_SESSION_KEY] = form.participant.pk
        rotate_token(request)
        return redirect("catalog:ideas")
    return render(request, "participants/login.html", {"form": form})


@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    request.session.pop(PARTICIPANT_SESSION_KEY, None)
    request.session.cycle_key()
    rotate_token(request)
    return redirect("catalog:ideas")
