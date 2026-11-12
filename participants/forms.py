from django import forms

from participants.models import User
from passwords import verify_password


class ParticipantLoginForm(forms.Form):
    name = forms.CharField(
        label="Имя участника", max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Пароль", strip=False, max_length=1024,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}),
    )

    participant: User | None = None

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        password = cleaned_data.get("password")
        if name and password:
            participant = User.objects.filter(name=name).first()
            if (
                participant is None
                or participant.password == "!"
                or not verify_password(participant.password, password)
            ):
                raise forms.ValidationError("Неверное имя или пароль.")
            self.participant = participant
        return cleaned_data
