from django.urls import path

from forge.views import (
    index,
    welcome,
    WorkerRegistrationView,
    WorkerDetailView,
    TaskListView,
    TeamCreateView,
    TeamDetailView,
    ProjectCreateView,
    ProjectDetailView, TaskCreateView, ProjectListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome"),
    path("register/", WorkerRegistrationView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("team/create/", TeamCreateView.as_view(), name="team-create"),
    path("team/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("project/create/", ProjectCreateView.as_view(), name="project-create"),
    path("project/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("project/task/create/", TaskCreateView.as_view(), name="project-task-create"),
    path("projects/", ProjectListView.as_view(), name="project-list"),

]

app_name = "forge"
