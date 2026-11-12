from django import forms

from catalog.models import Idea
from catalog.parameters import MAX_PARAMETER_VALUE
from participants.models import User
from taxonomy.models import Category


class AvailableIdeaFilterForm(forms.Form):
    q = forms.CharField(
        label="Название, описание или язык",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Например, Трекер"}),
    )
    category = forms.IntegerField(
        label="Язык", required=False, min_value=1, max_value=MAX_PARAMETER_VALUE,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, data=None):
        if data is not None and "q" in data:
            data = data.copy()
            data["q"] = data["q"].strip()
        super().__init__(data)
        self.fields["category"].widget.choices = [
            ("", "Все языки"), *Category.objects.values_list("pk", "name"),
        ]


class IdeaFilterForm(AvailableIdeaFilterForm):
    author = forms.IntegerField(
        label="Автор", required=False, min_value=1, max_value=MAX_PARAMETER_VALUE,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        label="Статус", required=False,
        choices=[("", "Любой"), *Idea.Status.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    created_at = forms.DateField(
        label="Дата создания", required=False, input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}),
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False, initial="newest",
        choices=[
            ("newest", "Сначала новые"),
            ("oldest", "Сначала старые"),
            ("title", "По названию"),
            ("category", "По языку и названию"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, data=None):
        super().__init__(data)
        self.fields["q"].label = "Фрагмент названия"
        self.fields["author"].widget.choices = [
            ("", "Все авторы"), *User.objects.values_list("pk", "name"),
        ]

    def clean_sort(self) -> str:
        sort = self.cleaned_data["sort"]
        if "sort" in self.data and not sort:
            raise forms.ValidationError("Выберите доступный порядок сортировки.")
        return sort or "newest"


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ("title", "description", "category", "image")
        labels = {"category": "Язык программирования", "image": "Иллюстрация"}
        help_texts = {
            "description": "Опишите задачу проекта и его основные возможности.",
            "image": "Необязательный файл в формате JPEG, PNG или WebP до 5 МБ.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control", "accept": "image/jpeg,image/png,image/webp",
            }),
        }

    def clean_image(self):
        image = self.cleaned_data["image"]
        if not image or "image" not in self.files:
            return image
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Размер изображения не должен превышать 5 МБ.")
        if image.image.format not in {"JPEG", "PNG", "WEBP"}:
            raise forms.ValidationError("Выберите изображение в формате JPEG, PNG или WebP.")
        return image


class SelectIdeaForm(forms.Form):
    def __init__(self, data, *, idea: Idea, participant: User):
        super().__init__(data)
        self.idea = idea
        self.participant = participant

    def clean(self):
        cleaned_data = super().clean()
        if not self.idea.is_available:
            raise forms.ValidationError("Эту идею уже выбрали.")
        if self.participant.selected_ideas.taken().exists():
            raise forms.ValidationError("Вы уже выбрали идею. Сначала освободите её.")
        return cleaned_data
