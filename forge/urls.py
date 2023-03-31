from django.urls import path

from forge.views import (
    index,
    welcome,
    WorkerRegistrationView,
    WorkerListView,
    WorkerDetailView,
    WorkerHireView,
    TaskCreateView,
    TaskDetailView,
    TaskListView,
    complete_task,
    TeamCreateView,
    TeamDetailView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    complete_project,
)

urlpatterns = [
    path("", index, name="index"),
    path("unregistered/", welcome, name="welcome"),
    path("register/", WorkerRegistrationView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/complete/", complete_task, name="complete-task"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("workers/<int:pk>/hire", WorkerHireView.as_view(), name="worker-hire"),
    path("team/create/", TeamCreateView.as_view(), name="team-create"),
    path("team/<int:pk>/", TeamDetailView.as_view(), name="team-detail"),
    path("project/create/", ProjectCreateView.as_view(), name="project-create"),
    path("project/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("project/<int:pk>/complete", complete_project, name="complete-project"),
    path("project/task/create/", TaskCreateView.as_view(), name="project-task-create"),
    path("projects/", ProjectListView.as_view(), name="project-list"),

]

app_name = "forge"
