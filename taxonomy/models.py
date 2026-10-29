"""Модель категории программных проектов."""
from django.db import models


class Category(models.Model):
    """Язык программирования, объединяющий идеи каталога."""

    name = models.CharField("Язык программирования", max_length=100, unique=True)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name
