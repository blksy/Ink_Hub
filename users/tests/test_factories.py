from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.models import ProfessionalProfile
from users.factories import UserFactory


User = get_user_model()


class UserFactoryTests(TestCase):
    def test_factory_creates_client(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.assertEqual(user.email, "client@example.com")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertTrue(
            User.objects.filter(email="client@example.com").exists()
        )

    def test_factory_does_not_create_professional_profile_for_client(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.assertFalse(
            ProfessionalProfile.objects.filter(user=user).exists()
        )

    def test_factory_creates_professional_with_profile(self):
        user = UserFactory.create_user(
            email="artist@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
       )

        self.assertEqual(user.role, User.Role.PROFESSIONAL)

        self.assertTrue(
            ProfessionalProfile.objects.filter(user=user).exists()
       )

    def test_factory_hashes_password(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
       )

        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.check_password("testpass123"))