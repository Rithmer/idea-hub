"""Конфигурация Django-приложения каталога идей."""
from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Регистрирует приложение каталога и тип автоматически создаваемых ключей."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
