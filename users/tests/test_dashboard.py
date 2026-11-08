
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from clients.models import ClientProfile
from users.models import User


class AccountDashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="dashboard@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )
        self.url = reverse("users:dashboard")

    def test_authenticated_user_can_access_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/dashboard.html")

    def test_anonymous_user_cannot_access_dashboard(self):
        response = self.client.get(self.url)

        login_url = resolve_url(settings.LOGIN_URL)

        expected_url = redirect_to_login(
            self.url,
            login_url=login_url,
        ).url

        self.assertRedirects(
            response,
            expected_url,
        )

    def test_user_without_client_profile_sees_activation_button(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        activation_url = reverse(
            "clients:client-profile-activate"
        )

        self.assertContains(
            response,
            f'action="{activation_url}"',
        )

        self.assertNotContains(
            response,
            f'href="{reverse("clients:client-profile")}"',
        )

    def test_user_with_client_profile_sees_profile_link(self):
        ClientProfile.objects.create(user=self.user)

        self.client.force_login(self.user)

        response = self.client.get(self.url)

        profile_url = reverse("clients:client-profile")
        activation_url = reverse(
            "clients:client-profile-activate"
        )

        self.assertContains(
            response,
            f'href="{profile_url}"',
        )

        self.assertNotContains(
            response,
            f'action="{activation_url}"',
        )
