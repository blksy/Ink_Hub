from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import ProfessionalProfile


User = get_user_model()

class RegisterViewTests(TestCase):
    def test_register_view_returns_200(self):
        response = self.client.get(
            reverse("users:register")
        )

        self.assertEqual(response.status_code, 200)

    def test_register_view_uses_correct_template(self):
        response = self.client.get(
            reverse("users:register")
        )

        self.assertTemplateUsed(
            response,
            "users/register.html",
        )

    def test_register_client_creates_user(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "newclient@example.com",
                "role": User.Role.CLIENT,
                "password1": "InkHubTest2026!x",
                "password2": "InkHubTest2026!x",
            },
        )

        self.assertTrue(
            User.objects.filter(
                email="newclient@example.com"
            ).exists()
        )

        self.assertEqual(response.status_code, 302)

    def test_register_professional_creates_user_and_professional_profile(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "newartist@example.com",
                "role": User.Role.PROFESSIONAL,
                "password1": "InkHubTest2026!x",
                "password2": "InkHubTest2026!x",
            },
        )

        user = User.objects.get(
            email="newartist@example.com"
        )

        self.assertEqual(user.role, User.Role.PROFESSIONAL)

        self.assertTrue(
            ProfessionalProfile.objects.filter(user=user).exists()
        )

        self.assertEqual(response.status_code, 302)

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "invalid@example.com",
                "role": User.Role.CLIENT,
                "password1": "InkHubTest2026!x",
                "password2": "DifferentPassword2026!x",
            },
        )

        self.assertFalse(
            User.objects.filter(
                email="invalid@example.com"
            ).exists()
        )

        self.assertEqual(response.status_code, 200)

class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.password = "InkHubTest2026!x"
        self.user = User.objects.create_user(
            email="login@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )

    def test_user_can_login_with_email(self):
        response = self.client.post(
            reverse("users:login"),
            data={
                "username": "login@example.com",
                "password": self.password,
            },
        )

        self.assertRedirects(
            response,
            reverse("professionals:professional-list"),
        )

        self.assertTrue(
            "_auth_user_id" in self.client.session
        )

    def test_invalid_login_does_not_authenticate_user(self):
        response = self.client.post(
            reverse("users:login"),
            data={
                "username": "login@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            "_auth_user_id" in self.client.session
        )

    def test_user_can_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("users:logout")
        )

        self.assertRedirects(
            response,
            reverse("users:login"),
        )

        self.assertFalse(
            "_auth_user_id" in self.client.session
        )

    def test_authenticated_user_cannot_access_register(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("users:register")
        )

        self.assertRedirects(
            response,
            reverse("professionals:professional-list"),
        )