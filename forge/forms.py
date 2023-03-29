from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Worker, Position, Team


class WorkerRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "E-mail"})
    )

    first_name = forms.TextInput()

    last_name = forms.TextInput()

    salary = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wanted salary"})
    )

    about = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Skills and anything about you", "rows": "3"})
    )

    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    status = forms.ChoiceField(
        choices=Worker.STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"})
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "salary",
            "about",
            "hire_date",
            "position",
            "status",
            "team"
        ]
