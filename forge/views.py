from typing import Tuple, Any

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, F, OuterRef, Count, Subquery, Q
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views import generic

from forge.forms import (
    ProjectForm,
    TaskForm,
    TaskSearchForm,
    TeamForm,
    WorkerSearchForm,
    WorkerRegisterForm,
    WorkerHireForm,
)
from forge.models import Worker, Task, Team, Project


def user_is_manager_or_admin(user: Any) -> bool | Any:
    return (user.is_authenticated
            and str(user.position) == "ProjectManager"
            or user.is_superuser)


def welcome(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("forge:index"))
    return render(request, "forge/unregistered/welcome.html")


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""
    worker_query = Worker.objects.all()
    tasks_query = Task.objects.all()

    num_users = worker_query.count()
    num_workers = worker_query.filter(status__gt=0).count()
    tasks_overall = tasks_query.count()
    tasks_done = tasks_query.filter(is_completed=True).count()

    teams = Team.objects.prefetch_related("members__tasks")

    max_tasks_done, best_team = get_max_tasks_done(teams)

    context = {
        "num_users": num_users,
        "num_workers": num_workers,
        "tasks_overall": tasks_overall,
        "tasks_done": tasks_done,
        "teams": teams.count(),
        "best_team": best_team,
        "max_tasks_done": max_tasks_done,
    }

    return render(request, "forge/index.html", context=context)


@require_POST
def complete_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = True
    task.save()
    return redirect("forge:task-detail", pk=pk)


def edit_task(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    if user_is_manager_or_admin(user):
        if request.method == "POST":
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                messages.success(request, "Task updated successfully!")
                return redirect("forge:task-detail", pk=pk)
        else:
            form = TaskForm(instance=task)
        return render(request, "forge/edit_task.html", {"form": form, "task": task})
    else:
        messages.error(request, "You do not have permission to edit this task.")
        return redirect("forge:view-task", pk=pk)


@require_POST
def complete_project(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    project.is_completed = True
    project.save()
    return redirect("forge:project-detail", pk=pk)


def worker_change(request, pk) -> Any:
    worker = get_object_or_404(Worker, pk=pk)

    if request.method == "POST":
        if user_is_manager_or_admin(request.user):
            form = WorkerHireForm(request.POST, instance=worker)
            if form.is_valid():
                form.save()
                return redirect("forge:worker-list")
        else:
            form = WorkerHireForm(instance=worker)
    else:
        form = WorkerHireForm(instance=worker)

    return render(request, "forge/worker_change.html", {"form": form, "worker": worker})


class WorkerRegistrationView(generic.CreateView):
    FIELDS_TO_POP = ["hire_date", "position", "status", "team"]
    model = get_user_model()
    form_class = WorkerRegisterForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> Any:
        if request.user.is_authenticated:
            return redirect("forge:task-list")  # refactor this after everything provided
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class: Any = None) -> Any:
        form = super().get_form(form_class)
        for field in self.FIELDS_TO_POP:
            form.fields.pop(field)
        return form


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm

    def get_success_url(self) -> str:
        return reverse_lazy("forge:task-list")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "tasks"
    paginate_by = 7

    def get_queryset(self) -> QuerySet:
        queryset = Task.objects.prefetch_related("project", "workers").filter(
            project__is_completed=False
        )
        title = self.request.GET.get("title", "")
        user = self.request.user
        sort_by = self.request.GET.get("sort")

        if title:
            queryset = queryset.filter(
                title__icontains=title,
            )

        if sort_by:
            last_sort_field = self.request.session.get("last_sort_field")
            last_sort_order = self.request.session.get("last_sort_order")

            if sort_by == last_sort_field:
                sort_order = "-" + last_sort_order if last_sort_order == "" else ""
            else:
                sort_order = ""

            self.request.session["last_sort_field"] = sort_by
            self.request.session["last_sort_order"] = sort_order

            if sort_by == "title":
                queryset = queryset.order_by(sort_order + "title")
            elif sort_by == "deadline":
                queryset = queryset.order_by(sort_order + "deadline")
            elif sort_by == "priority":
                queryset = queryset.order_by(sort_order + "priority")
            elif sort_by == "tag":
                queryset = queryset.order_by(sort_order + "tag__name")

        if user_is_manager_or_admin(user):
            return queryset

        return queryset.filter(
            is_completed=False,
            workers__id=user.id,
        )

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data()
        title = self.request.GET.get("title", "")

        context["search_form"] = TaskSearchForm(initial={"title": title})
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.prefetch_related("workers__teams")


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    context_object_name = "workers"
    paginate_by = 5

    def get_queryset(self) -> QuerySet:
        queryset = (get_user_model()
                    .objects.select_related("position")
                    .filter(~Q(position__name="ProjectManager"))
                    )
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(first_name__icontains=name)
        return queryset

    def get_context_data(
        self, *, object_list: QuerySet = None, **kwargs
    ) -> dict[str, Any]:
        context = super().get_context_data()
        name = self.request.GET.get("name", "")

        context["search_form"] = WorkerSearchForm(initial={"name": name})
        return context


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return queryset.select_related("team", "position")

    def get_object(self, queryset=None) -> Any:
        pk = self.kwargs.get("pk")
        worker = get_user_model().objects.get(pk=pk)
        return worker


@method_decorator(user_passes_test(user_is_manager_or_admin), name="dispatch")
class WorkerHireView(generic.UpdateView):
    queryset = Worker.objects.all()
    form_class = WorkerHireForm
    template_name = "forge/worker_hire.html"

    def get_success_url(self) -> str:
        return reverse_lazy("forge:worker-detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form: Any) -> HttpResponse:
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


@method_decorator(user_passes_test(user_is_manager_or_admin), name="dispatch")
class TeamCreateView(generic.CreateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy("forge:team-list")

    def dispatch(self, request, *args, **kwargs) -> Any:
        return super().dispatch(request, *args, **kwargs)


@method_decorator(user_passes_test(user_is_manager_or_admin), name="dispatch")
class TeamUpdateView(generic.UpdateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy("forge:team-list")

    def dispatch(self, request, *args, **kwargs) -> Any:
        return super().dispatch(request, *args, **kwargs)


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    queryset = Team.objects.prefetch_related("members")
    context_object_name = "teams"


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    queryset = Team.objects.prefetch_related("members")
    context_object_name = "team"


@method_decorator(user_passes_test(user_is_manager_or_admin), name="dispatch")
class ProjectCreateView(generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "forge/project_form.html"
    success_url = reverse_lazy("forge:project-list")

    def get_context_data(self, **kwargs) -> dict[str | Any]:
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    context_object_name = "project"
    queryset = Project.objects.prefetch_related("tasks__workers")


@method_decorator(user_passes_test(user_is_manager_or_admin), name="dispatch")
class ProjectUpdateView(generic.UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "forge/project_form.html"
    success_url = reverse_lazy("forge:project-list")

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        self.object.is_completed = False
        self.object.save()
        return response

    def get_context_data(self, **kwargs) -> dict[str | Any]:
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project

    def get_queryset(self) -> QuerySet:
        user = get_user_model().objects.get(id=self.request.user.id)
        if user.position == "ProjectManager":
            return super().get_queryset().filter(manager=self.request.user)
        return super().get_queryset()


def get_max_tasks_done(teams: QuerySet) -> Tuple[int, str] | Tuple[int, None]:
    subquery = (
        Task.objects.filter(workers__team=OuterRef("pk"))
        .values("workers__teams__id")
        .annotate(total_tasks_done=Count("pk"))
        .values("total_tasks_done")[:1]
    )

    team_totals = (
        teams.annotate(total_tasks_done=Subquery(subquery), team_name=F("name"))
        .values("total_tasks_done", "team_name")
        .order_by("-total_tasks_done", "team_name")
    ).distinct()

    if not team_totals:
        return 0, None

    best_team = team_totals.first()
    return best_team["total_tasks_done"], best_team["team_name"]
