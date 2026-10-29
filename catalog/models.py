"""Модель идеи, связи и ограничения целостности."""
from django.db import models
from django.utils import timezone


class Idea(models.Model):
    """Идея проекта с категорией, автором и необязательным выбравшим участником."""

    class Status(models.TextChoices):
        """Допустимые состояния идеи: свободна или выбрана участником."""

        AVAILABLE = "не взята", "Свободна"
        TAKEN = "взята", "Взята"

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    category = models.ForeignKey(
        "taxonomy.Category", on_delete=models.PROTECT,
        related_name="ideas", verbose_name="Категория",
    )
    author = models.ForeignKey(
        "participants.User", on_delete=models.PROTECT,
        related_name="authored_ideas", verbose_name="Автор",
    )
    status = models.CharField(
        "Статус", max_length=10, choices=Status.choices, default=Status.AVAILABLE,
    )
    selected_by = models.ForeignKey(
        "participants.User", on_delete=models.PROTECT, null=True, blank=True,
        related_name="selected_ideas", verbose_name="Выбрал",
    )
    created_at = models.DateField("Дата создания", default=timezone.localdate)

    class Meta:
        ordering = ("-created_at", "-pk")
        verbose_name = "Идея"
        verbose_name_plural = "Идеи"
        indexes = [models.Index(fields=["status", "created_at"], name="idea_status_date")]
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(status="не взята", selected_by__isnull=True)
                           | models.Q(status="взята", selected_by__isnull=False)),
                name="idea_status_selection_consistent",
            ),
            models.UniqueConstraint(
                fields=["selected_by"],
                condition=models.Q(selected_by__isnull=False),
                name="one_selected_idea_per_user",
            ),
        ]

    @property
    def is_available(self) -> bool:
        """Проверяет, свободна ли идея для выбора участником."""
        return self.status == self.Status.AVAILABLE

    def __str__(self) -> str:
        return self.title
