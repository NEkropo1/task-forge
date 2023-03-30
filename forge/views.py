from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from forge.forms import WorkerRegisterForm, TeamForm, ProjectCreateForm, TaskForm, TaskSearchForm
from forge.models import Worker, Task, Team, Project


# Create your views here.
def welcome(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("forge:index"))
    return render(request, "forge/unregistered/welcome.html")


@login_required
def index(request):
    """View function for the home page of the site."""

    num_workers = Worker.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_workers": num_workers,
        "num_visits": num_visits,
    }

    return render(request, "forge/index.html", context=context)


class WorkerRegistrationView(generic.CreateView):
    FIELDS_TO_POP = ["hire_date", "position", "status", "team"]
    model = get_user_model()
    form_class = WorkerRegisterForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("forge:task-list")  # refactor this after everything provided
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in self.FIELDS_TO_POP:
            form.fields.pop(field)
        return form


class TaskCreateView(generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "forge/task_form.html"

    def get_success_url(self):
        return reverse_lazy("forge:task-list")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = Task.objects.prefetch_related("workers")
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(title__icontains=name)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context["search_form"] = TaskSearchForm()
        return context


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("team", "position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.get_object()
        if worker.position and worker.position.name == "ProjectManager":
            context["project_task_create_url"] = reverse_lazy("project-task-create")
        return context


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    context_object_name = "team"


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectCreateForm
    template_name = "forge/project_form.html"


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    context_object_name = "project"


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project

    def get_queryset(self) -> None:
        query = super().get_queryset().filter(id=self.request.user.id)
        print(query)
        return query
