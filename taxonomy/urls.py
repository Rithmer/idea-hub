"""Именованные маршруты категорий."""
from django.urls import path

from . import views


app_name = "taxonomy"


urlpatterns = [
    path("", views.categories, name="categories"),
    path("<int:category_id>/", views.category_detail, name="category_detail"),
]
