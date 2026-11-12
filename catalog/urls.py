"""Именованные маршруты каталога идей."""
from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.ideas, name="ideas"),
    path("available/", views.available_ideas, name="available"),
    path("selected/", views.selected_ideas, name="selected"),
    path("authors/", views.authors, name="authors"),
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.idea_create, name="idea_create"),
    path("<int:idea_id>/", views.idea_detail, name="idea_detail"),
    path("<int:idea_id>/edit/", views.idea_edit, name="idea_edit"),
    path("<int:idea_id>/select/", views.idea_select, name="idea_select"),
    path("<int:idea_id>/release/", views.idea_release, name="idea_release"),
]
