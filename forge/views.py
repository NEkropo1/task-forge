from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from forge.forms import WorkerRegisterForm
from forge.models import Worker


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
            return redirect("forge:index")  # refactor this after everything provided
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in self.FIELDS_TO_POP:
            form.fields.pop(field)
        return form
