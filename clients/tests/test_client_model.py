from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

from clients.models import ClientProfile


User = get_user_model()


class ClientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT
        )

    def test_create_client_profile(self):
        profile = ClientProfile.objects.create(
            user=self.user,
        )

        self.assertEqual(self.user, profile.user)

    def test_client_profile_string_representation(self):
        self.user.first_name = "Jan"
        self.user.last_name = "Kowalski"
        self.user.save()

        profile = ClientProfile.objects.create(user=self.user)

        self.assertEqual(str(profile), "Jan Kowalski")

        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save()

        self.assertEqual(str(profile), "client@example.com")

    def test_professional_can_have_client_profile(self):
        professional = User.objects.create_user(
            email="professional@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL
        )

        profile = ClientProfile.objects.create(user = professional)
        professional.refresh_from_db()
        
        self.assertEqual(professional.role, User.Role.PROFESSIONAL)
        
        self.assertEqual(profile.user, professional)

    def test_client_profile_cascade_delete(self):
        profile = ClientProfile.objects.create(user=self.user)
        profile_id = profile.pk

        self.user.delete()

        self.assertFalse(ClientProfile.objects.filter(pk=profile_id).exists())

    def test_client_profile_unique_user(self):
        ClientProfile.objects.create(user = self.user)

        with self.assertRaises(IntegrityError):
            ClientProfile.objects.create(user = self.user)