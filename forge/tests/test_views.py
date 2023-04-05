# flake8: noqa E501, F401, F821, ANN003, ANN001, ANN002, ANN101, ANN201
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from forge.models import Position, Team, Worker
from forge.views import user_is_manager_or_admin

TEST_REGISTERED_URLS = [
    reverse("forge:index"),
    reverse("forge:worker-detail", args=[1]),
    reverse("forge:worker-list"),
    reverse("forge:welcome"),
    reverse("forge:project-list"),
    reverse("forge:task-list"),
    reverse("forge:project-detail", args=[1]),
    reverse("forge:worker-detail", args=[1]),
]


class WelcomeViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass12345"
        )

    def test_welcome_view_redirects_to_index_if_authenticated(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("forge:welcome"))
        self.assertRedirects(response, reverse("forge:index"))

    def test_welcome_view_renders_correct_template_if_not_authenticated(self) -> None:
        response = self.client.get(reverse("forge:index"))
        self.assertRedirects(response, reverse("forge:welcome") + "?next=%2F")


class TestTeamViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass12345"
        )
        self.position = Position.objects.create(name="ProjectManager")
        self.worker = get_user_model().objects.create(
            email="pm@test.com", position=self.position
        )
        self.team = Team.objects.create(name="Test Team", project_manager=self.worker)

    def test_team_detail_view(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("forge:team-detail", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)

    def test_team_detail_unregistered_view(self) -> None:
        response = self.client.get(reverse("forge:team-detail", args=[self.user.id]))
        self.assertEqual(response.status_code, 302)


class WorkerHireViewTestCase(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.position = Position.objects.create(name="Developer")
        self.team_manager = Worker.objects.create(
            username="manager1",
            email="manager1@example.com",
            password="testpass",
            position=self.position,
            status=Worker.FREE_AGENT,
        )
        self.team = Team.objects.create(name="Team A", project_manager=self.team_manager)
        self.worker = Worker.objects.create(
            username="worker1",
            email="worker1@example.com",
            password="testpass",
            position=self.position,
            status=Worker.FREE_AGENT,
        )

    def test_form_valid(self) -> None:
        self.client.login(username="testuser", password="testpass")
        url = reverse("forge:worker-hire", kwargs={"pk": self.worker.pk})
        data = {
            "email": "newworker@example.com",
            "salary": 5000,
            "hire_date": "2023-03-28",
            "position": self.position.pk,
            "status": Worker.IN_TEAM,
            "team": self.team.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("forge:worker-detail", kwargs={"pk": self.worker.pk})
        )
        worker = Worker.objects.get(pk=self.worker.pk)
        self.assertEqual(worker.email, data["email"])
        self.assertEqual(worker.salary, data["salary"])
        self.assertEqual(worker.hire_date.strftime("%Y-%m-%d"), data["hire_date"])
        self.assertEqual(worker.position, self.position)
        self.assertEqual(worker.status, Worker.IN_TEAM)
        self.assertEqual(worker.team, self.team)

    def test_form_invalid(self) -> None:
        self.client.login(username="testuser", password="testpass")
        url = reverse("forge:worker-hire", kwargs={"pk": self.worker.pk})
        data = {
            "email": "newworker@example.com",
            "salary": "invalid",
            "hire_date": "2023-03-28",
            "position": self.position.pk,
            "status": Worker.IN_TEAM,
            "team": self.team.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"salary": ["Enter a whole number."]})


class UserIsManagerOrAdminTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.pm = Position.objects.create(
            name="ProjectManager"
        )
        self.position_worker = Position.objects.create(
            name="worker"
        )
        self.admin_user = self.User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpassword",
        )
        self.manager_user = self.User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="testpassword",
            position=self.pm
        )
        self.worker_user = self.User.objects.create_user(
            username="worker",
            email="worker@example.com",
            password="testpassword",
            position=self.position_worker
        )

    def test_user_is_manager_or_admin_authenticated_admin_user(self):
        result = user_is_manager_or_admin(self.admin_user)
        self.assertTrue(result)

    def test_user_is_manager_or_admin_authenticated_manager_user(self):
        result = user_is_manager_or_admin(self.manager_user)
        self.assertTrue(result)

    def test_user_is_manager_or_admin_authenticated_worker_user(self):
        result = user_is_manager_or_admin(self.worker_user)
        self.assertFalse(result)


    def test_user_is_manager_or_admin_unauthenticated_user(self):
        try:
            user_is_manager_or_admin(None)
        except AttributeError:
            pass
