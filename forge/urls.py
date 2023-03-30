from django.urls import path

from forge.views import (
    index,
    welcome,
    WorkerRegistrationView,
    WorkerDetailView,
    TeamCreateView,
    TaskListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome"),
    path("register/", WorkerRegistrationView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("team/create/", TeamCreateView.as_view(), name="team-create"),
]

app_name = "forge"
