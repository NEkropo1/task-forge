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
        ("1", "Urgent"),
        ("2", "High"),
        ("3", "Medium"),
        ("4", "Low"),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, blank=False)
    workers = models.ManyToManyField(
        "Worker", related_name="tasks", through="TaskAssignment"
    )
    tag = models.ForeignKey(TaskType, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)
    assignee = models.ForeignKey(
        "Worker",
        on_delete=models.CASCADE,
        related_name="assignees"
    )
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="projects"
    )

    def __str__(self):
        return (
            f"{self.assignee.username} assigned "
            "to {self.task.title} on {self.assigned_date}"
        )


class Team(models.Model):
    name = models.CharField(max_length=110, unique=True)
    members = models.ManyToManyField("Worker", blank=True, related_name="teams")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            manager = Worker.objects.filter(position__name="Manager").first()
            if manager:
                self.members.add(manager)
        super(Team, self).save(*args, **kwargs)


class Position(models.Model):
    name = models.CharField(max_length=127, unique=True)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    NOT_WORKER = 0
    IN_TEAM = 1
    FREE_AGENT = 2
    STATUS_CHOICES = (
        (NOT_WORKER, "Not a worker"),
        (IN_TEAM, "In team"),
        (FREE_AGENT, "Free agent"),
    )

    email = models.EmailField(unique=True, blank=False, null=False)
    salary = models.PositiveIntegerField(blank=True, null=True)  # Coins
    about = models.TextField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=NOT_WORKER)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def get_absolute_url(self):
        return reverse("forge:worker-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    manager = models.ForeignKey(
        "ProjectManager",
        on_delete=models.CASCADE,
        related_name="projects"
    )
    is_completed = models.BooleanField(default=False)
    start_date = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )
    deadline = models.DateField(
        validators=[MinValueValidator(limit_value=datetime.date.today)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "manager"], name="unique_project_and_manager",
            )
        ]

    def __str__(self):
        return self.name


class ProjectTaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project"
    )
    assignee = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="workers"
    )

    def __str__(self):
        return (
            f"{self.task.title} assigned to {self.project.name} "
            "on {self.project.start_date} by {self.assignee.username}"
        )


class ProjectManager(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="manager")

    def __str__(self):
        return str(self.worker.email)
