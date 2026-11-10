from django.test import TestCase

from clients.models import ClientProfile
from clients.services import create_client_profile
from users.models import User


class ClientProfileServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="professional@example.com",
            password="TestPassword123!",
            first_name="Anna",
            last_name="Nowak",
            role=User.Role.PROFESSIONAL,
        )

    def test_professional_can_create_client_profile(self):
        profile = create_client_profile(self.user)

        self.assertIsInstance(profile, ClientProfile)
        self.assertEqual(profile.user, self.user)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.role,
            User.Role.PROFESSIONAL,
        )

    def test_creating_client_profile_twice_does_not_duplicate(self):
        first_profile = create_client_profile(self.user)
        second_profile = create_client_profile(self.user)

        self.assertEqual(first_profile.pk, second_profile.pk)

        self.assertEqual(
            ClientProfile.objects.filter(user=self.user).count(),
            1,
        )