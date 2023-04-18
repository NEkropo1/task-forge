# flake8: noqa E501, F401, F821, ANN003, ANN001, ANN002, ANN101, ANN201
from django import template
from django.http import HttpRequest, HttpResponse

register = template.Library()


@register.simple_tag
def query_transform(request: HttpRequest, **kwargs) -> HttpResponse:
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, 0)

    return updated.urlencode()
