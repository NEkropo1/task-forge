from django.urls import path

from forge.views import (
    index,
    welcome,
    WorkerRegistrationView,
    WorkerDetailView,
    TaskListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome"),
    path("register/", WorkerRegistrationView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
]

app_name = "forge"
