"""Администрирование идей и просмотр связей из карточек каталога."""
from django.contrib import admin

from catalog.models import Idea


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "selected_by", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "description", "category__name", "author__name", "selected_by__name")
    ordering = ("-created_at", "-pk")
    list_per_page = 20
    list_select_related = ("category", "author", "selected_by")
    autocomplete_fields = ("category", "author", "selected_by")


class IdeaInline(admin.TabularInline):
    """Показывает связи и ведёт в полную форму редактирования идеи."""

    model = Idea
    fields = readonly_fields = ("title", "status", "created_at")
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
