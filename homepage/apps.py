"""Конфигурация Django-приложения главной страницы."""
from django.apps import AppConfig


class HomepageConfig(AppConfig):
    """Регистрирует приложение главной страницы."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "homepage"
