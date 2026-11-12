from django.urls import path

from participants import views


app_name = "participants"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]
