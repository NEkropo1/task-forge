import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Worker, Position, Team, Project, TaskType, Task


class ProjectCreateForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    manager = forms.ModelChoiceField(
        queryset=Worker.objects.filter(position__name="ProjectManager"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
    )

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "manager",
            "start_date",
            "deadline",
        ]

    def clean(self) -> None:
        manager = self.cleaned_data.get("manager")
        if manager and manager.position.name != "ProjectManager":
            raise ValidationError("Manager must have position of ProjectManager.")

        super().clean()


class WorkerHireForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "E-mail"}))

    salary = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wanted salary"})
    )

    hire_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = forms.ChoiceField(
        choices=Worker.STATUS_CHOICES[1:],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=True,
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )

    class Meta:
        model = Worker
        fields = ["email", "salary", "hire_date", "position", "status", "team"]

    def clean(self) -> dict:
        team = self.cleaned_data.get("team")
        status = self.cleaned_data.get("status")

        if not team and str(status) == "1":
            raise ValidationError("Worker in a team can't be a 'free agent'")

        if str(status) == "2" and team:
            raise ValidationError(
                "Worker cannot be a 'free agent' " "if assigned to a team."
            )

        return self.cleaned_data


class WorkerRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "E-mail"}))

    first_name = forms.TextInput()

    last_name = forms.TextInput()

    salary = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wanted salary"})
    )

    about = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Skills and anything about you", "rows": "3"}
        )
    )

    hire_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = forms.ChoiceField(
        choices=Worker.STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all(), widget=forms.Select(attrs={"class": "form-select"})
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
            "team",
        ]


class WorkerSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search workers by name",
            }
        ),
    )


class TaskSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search tasks here",
            }
        ),
    )


class TaskForm(forms.ModelForm):
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.prefetch_related("tasks__tag").filter(status__gt=0),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    tag = forms.ModelChoiceField(
        queryset=TaskType.objects.all(), empty_label=None, label="Task Type"
    )
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        validators=[MinValueValidator(limit_value=datetime.date.today)],
    )

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        empty_label=None,
        required=True,
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "deadline",
            "is_completed",
            "priority",
            "workers",
            "tag",
            "project",
        ]


class TeamForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    forms.ModelChoiceField(
        queryset=Worker.objects.select_related("position").filter(
            position__name__icontains="ProjectManager"
        ),
        required=False,
        empty_label=None,
        label="Project Manager",
    )

    class Meta:
        model = Team
        fields = ["name", "project_manager", "members"]
