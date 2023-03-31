# flake8: noqa E501, F401, F821, ANN003, ANN101, ANN201
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views import generic

from forge.forms import (
    WorkerRegisterForm,
    TeamForm,
    ProjectCreateForm,
    TaskForm,
    TaskSearchForm,
    WorkerSearchForm,
    WorkerHireForm
)
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


@require_POST
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = True
    task.save()
    return redirect("forge:task-detail", pk=pk)


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


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy("forge:task-list")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "tasks"
    paginate_by = 7

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


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    context_object_name = "workers"
    paginate_by = 10

    def get_queryset(self):
        queryset = get_user_model().objects.select_related("position")
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(first_name__icontains=name)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        name = self.request.GET.get("name", "")

        context["search_form"] = WorkerSearchForm(initial={
            "name": name
        })
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related("workers__teams")


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("team", "position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.get_object()
        if worker.position and worker.position.name == "ProjectManager":
            context["project_task_create_url"] = reverse_lazy("project-task-create")
        return context


class WorkerHireView(LoginRequiredMixin, generic.UpdateView):
    queryset = Worker.objects.all()
    form_class = WorkerHireForm
    template_name = "forge/worker_hire.html"

    def get_success_url(self):
        return reverse_lazy("forge:worker-detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        response = super().form_valid(form)
        worker = form.save(commit=False)
        worker.team = form.cleaned_data["team"]
        worker.status = form.cleaned_data["status"]
        try:
            form.full_clean()
        except ValidationError:
            return self.form_invalid(form)
        else:
            worker.save()
            return response


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    queryset = Team.objects.prefetch_related("members")
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
