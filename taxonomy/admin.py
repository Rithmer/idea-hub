"""Администрирование языков программирования."""
from django.contrib import admin

from catalog.admin import IdeaInline
from taxonomy.models import Category


class CategoryIdeaInline(IdeaInline):
    fk_name = "category"
    verbose_name_plural = "Идеи в категории"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name", "pk")
    list_per_page = 20
    inlines = (CategoryIdeaInline,)
