from django import template
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

register = template.Library()


@register.filter
def filter_by_completion(queryset: QuerySet, condition: str) -> QuerySet:
    if condition == "+":
        return queryset.filter(is_completed=True)
    if condition == "-":
        return queryset.filter(is_completed=False)
    raise ValidationError("Invalid condition. Must be '+' or '-'.")
