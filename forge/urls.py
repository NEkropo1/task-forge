from django.urls import path

from forge.views import index, welcome, WorkerRegistrationView

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome"),
    path("register/", WorkerRegistrationView.as_view(), name="register"),
]

app_name = "forge"
