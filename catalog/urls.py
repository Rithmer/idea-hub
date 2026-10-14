from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    path("", views.ideas, name="ideas"),
    path("<int:idea_id>/", views.idea_detail, name="idea_detail"),
]
