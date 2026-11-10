from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.shortcuts import resolve_url
from django.contrib.auth.views import redirect_to_login

from artists.models import ProfessionalProfile
from clients.models import ClientProfile
from users.models import User


class ClientProfileActivationViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="professional@example.com",
            password="TestPassword123!",
            first_name="Anna",
            last_name="Nowak",
            role=User.Role.PROFESSIONAL,
        )

        self.url = reverse(
            "clients:client-profile-activate"
        )

    def test_authenticated_user_can_activate_client_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("clients:client-profile"),
        )

        self.assertTrue(
            ClientProfile.objects.filter(
                user=self.user
            ).exists()
        )

    def test_get_method_is_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

        self.assertFalse(
              ClientProfile.objects.filter(
                  user=self.user
               ).exists()
        )

    def test_anonymous_user_cannot_activate_profile(self):
        response = self.client.post(self.url)

        login_url = resolve_url(settings.LOGIN_URL)

        expected_url = redirect_to_login(
            self.url,
            login_url=login_url,
        ).url

        self.assertRedirects(
            response,
            expected_url,
        )

        self.assertEqual(
            ClientProfile.objects.count(),
            0,
        )

    def test_repeated_activation_does_not_create_duplicates(self):
        self.client.force_login(self.user)

        self.client.post(self.url)
        self.client.post(self.url)

        self.assertEqual(
            ClientProfile.objects.filter(
                user=self.user
            ).count(),
            1,
        )

    def test_activation_does_not_change_user_role(self):
        self.client.force_login(self.user)

        self.client.post(self.url)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.role,
            User.Role.PROFESSIONAL,
        )

    def test_activation_preserves_professional_profile(self):
        professional = ProfessionalProfile.objects.create(
            user=self.user
        )

        original_profile_id = professional.pk


        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("clients:client-profile"),
        )
 
   
        self.assertTrue(
            ClientProfile.objects.filter(
                user=self.user
            ).exists()
        )

        self.assertTrue(
            ProfessionalProfile.objects.filter(
                user=self.user
            ).exists()
        )

        professional_after = ProfessionalProfile.objects.get(
            user=self.user
        )

        self.assertEqual(
            professional_after.pk,
            original_profile_id,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.role,
            User.Role.PROFESSIONAL,
        )

    