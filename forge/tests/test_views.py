from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class WelcomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass12345")

    def test_welcome_view_redirects_to_index_if_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("forge:welcome"))
        self.assertRedirects(response, reverse("forge:index"))

    def test_welcome_view_renders_correct_template_if_not_authenticated(self):
        response = self.client.get(reverse("forge:welcome"))
        self.assertTemplateUsed(response, "forge/unregistered/welcome.html")
