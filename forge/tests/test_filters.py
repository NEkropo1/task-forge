import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from forge.models import Project, Task, Position, TaskType
from forge.templatetags.custom_filters import filter_by_completion


class FilterByCompletionTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(
            name="ProjectManager"
        )

        self.worker = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            position=self.position,
        )

        self.tag = TaskType.objects.create(
            name="testTAG"
        )

        self.project = Project.objects.create(
            name="Test Project",
            start_date=datetime.datetime.now(),
            deadline=datetime.datetime.now()
            + datetime.timedelta(days=1),
            manager=self.worker
        )

        self.task1 = Task.objects.create(
            project=self.project,
            title="Task 1",
            deadline=datetime.datetime.now(),
            tag=self.tag,
            is_completed=True
        )
        self.task2 = Task.objects.create(
            project=self.project,
            title="Task 2",
            deadline=datetime.datetime.now(),
            is_completed=False,
            tag=self.tag,
        )

    def test_filter_by_completion_plus(self):
        qs = Task.objects.all()
        filtered_qs = filter_by_completion(qs, "+")
        self.assertEqual(filtered_qs.count(), 1)
        self.assertTrue(self.task1 in filtered_qs)
        self.assertFalse(self.task2 in filtered_qs)

    def test_filter_by_completion_minus(self) -> None:
        qs = Task.objects.all()
        filtered_qs = filter_by_completion(qs, "-")
        self.assertEqual(filtered_qs.count(), 1)
        self.assertFalse(self.task1 in filtered_qs)
        self.assertTrue(self.task2 in filtered_qs)

    def test_filter_by_completion_invalid_condition(self) -> None:
        with self.assertRaises(ValidationError):
            qs = Task.objects.all()
            filter_by_completion(qs, "invalid_condition")
