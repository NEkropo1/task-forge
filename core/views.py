from django.shortcuts import render

from forge.models import Worker


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