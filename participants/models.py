"""Участники каталога идей."""
from django.db import models


class User(models.Model):
    """Участник каталога ПР7; учётные записи Django auth хранятся отдельно."""

    name = models.CharField("Имя", max_length=150, unique=True)
    password = models.CharField("Хеш пароля", max_length=255)
    is_admin = models.BooleanField("Администратор", default=False)

    class Meta:
        db_table = "catalog_user"
        ordering = ("name", "pk")
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self) -> str:
        return self.name
