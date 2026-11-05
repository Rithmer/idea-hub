"""Администрирование участников каталога и их связей с идеями."""
from django import forms
from django.contrib import admin

from catalog.admin import IdeaInline
from participants.models import User
from passwords import hash_password


class ParticipantForm(forms.ModelForm):
    new_password = forms.CharField(
        label="Новый пароль",
        max_length=255,
        strip=False,
        required=False,
        widget=forms.PasswordInput,
        help_text="При редактировании оставьте пустым, чтобы сохранить текущий пароль.",
    )

    class Meta:
        model = User
        fields = ("name", "is_admin", "new_password")

    def clean_new_password(self):
        password = self.cleaned_data["new_password"]
        if self.instance._state.adding and not password:
            raise forms.ValidationError("Введите пароль нового участника.")
        return password


class AuthoredIdeaInline(IdeaInline):
    fk_name = "author"
    verbose_name_plural = "Авторские идеи"


class SelectedIdeaInline(IdeaInline):
    fk_name = "selected_by"
    verbose_name_plural = "Выбранные идеи"


@admin.register(User)
class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantForm
    list_display = ("name", "is_admin")
    list_filter = ("is_admin",)
    search_fields = ("name",)
    ordering = ("name", "pk")
    list_per_page = 20
    inlines = (AuthoredIdeaInline, SelectedIdeaInline)

    def save_model(self, request, obj, form, change):
        password = form.cleaned_data["new_password"]
        if password:
            obj.password = hash_password(password)
        super().save_model(request, obj, form, change)
