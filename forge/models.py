from __future__ import annotations
import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = (
        ("U", "Urgent"),
        ("H", "High"),
        ("M", "Medium"),
        ("L", "Low"),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    assignees = models.ManyToManyField(
        "Worker", related_name="tasks", through="TaskAssignment"
    )
    tag = models.ForeignKey(TaskType, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assignee = models.ForeignKey("Worker", on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return (
            f"{self.assignee.username} assigned "
            "to {self.task.title} on {self.assigned_date}"
        )


class Team(models.Model):
    name = models.CharField(max_length=110)
    members = models.ManyToManyField("Worker", blank=True, related_name="teams")

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    email = models.EmailField(unique=True, required=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("forge:user-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    manager = models.ForeignKey("ProjectManager", on_delete=models.CASCADE, related_name="projects")
    start_date = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )
    deadline = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )

    def __str__(self):
        return self.name


class ProjectTaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(Worker, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.task.title} assigned to {self.project.name} "
            "on {self.project.start_date} by {self.assignee.username}"
        )


class ProjectManager(models.Model):
    worker = models.OneToOneField(Worker, on_delete=models.CASCADE)