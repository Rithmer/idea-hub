from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.ideas, name="ideas"),
    path("available/", views.available_ideas, name="available"),
    path("selected/", views.selected_ideas, name="selected"),
    path("authors/", views.authors, name="authors"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:idea_id>/", views.idea_detail, name="idea_detail"),
]
