from django import template
from django.db.models import QuerySet

register = template.Library()


@register.filter
def filter_by_completion(queryset: QuerySet, condition: str) -> QuerySet:
    if condition == "+":
        return queryset.filter(is_completed=True)
    return queryset.filter(is_completed=False)
