"""Конфигурация Django-приложения категорий."""
from django.apps import AppConfig


class TaxonomyConfig(AppConfig):
    """Регистрирует приложение категорий."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "taxonomy"
