from django.urls import path

from forge.views import index, welcome

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome")
]

app_name = "forge"
