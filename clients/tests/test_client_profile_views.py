
from django.test import TestCase
from django.urls import reverse

from clients.models import ClientProfile
from users.models import User


class ClientProfileDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="jan@example.com",
            password="TestPassword123!",
            first_name="Jan",
            last_name="Kowalski",
            role=User.Role.CLIENT,
        )

        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            phone_number="123456789",
        )

        self.url = reverse("clients:client-profile")

    def test_client_profile_url(self):
        """Sprawdza poprawność adresu URL."""
        self.assertEqual(self.url, "/clients/profile/")

    def test_login_required(self):
        """Niezalogowany użytkownik musi zostać przekierowany."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)

    def test_authenticated_user_can_access_profile(self):
        """Zalogowany klient może wyświetlić swój profil."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_view_returns_correct_client_profile(self):
        """Widok udostępnia profil zalogowanego użytkownika."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["client_profile"],
            self.client_profile,
        )

    def test_user_without_client_profile_gets_404(self):
        """Użytkownik bez profilu klienta otrzymuje HTTP 404."""
        professional = User.objects.create_user(
            email="artist@example.com",
            password="TestPassword123!",
            first_name="Adam",
            last_name="Nowak",
            role=User.Role.PROFESSIONAL,
        )

        self.client.force_login(professional)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_view_uses_correct_template(self):
        """Widok korzysta z właściwego szablonu."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertTemplateUsed(
            response,
            "clients/profile_detail.html",
        )

    
class ClientProfileUpdateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="jan@example.com",
            password="TestPassword123!",
            first_name="Jan",
            last_name="Kowalski",
            role=User.Role.CLIENT,
        )

        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            phone_number="123456789",
        )

        self.url = reverse("clients:client-profile-update")

    def test_login_required(self):
        """Niezalogowany użytkownik nie może edytować profilu."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)

    def test_authenticated_user_can_access_edit_form(self):
        """Zalogowany klient może otworzyć formularz edycji."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "clients/profile_edit.html",
        )
        self.assertEqual(
            response.context["form"].instance,
            self.client_profile,
        )

    def test_post_updates_user_and_client_profile(self):
        """POST aktualizuje dane User oraz ClientProfile."""
        self.client.force_login(self.user)

        form_data = {
            "first_name": "Adam",
            "last_name": "Nowak",
            "phone_number": "987654321",
        }

        response = self.client.post(self.url, data=form_data)

        self.assertRedirects(
            response,
            reverse("clients:client-profile"),
        )

        self.user.refresh_from_db()
        self.client_profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Adam")
        self.assertEqual(self.user.last_name, "Nowak")
        self.assertEqual(
            self.client_profile.phone_number,
            "987654321",
        )

    def test_user_without_client_profile_gets_404(self):
        """Użytkownik bez ClientProfile otrzymuje HTTP 404."""
        professional = User.objects.create_user(
            email="artist@example.com",
            password="TestPassword123!",
            first_name="Anna",
            last_name="Nowak",
            role=User.Role.PROFESSIONAL,
        )

        self.client.force_login(professional)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
