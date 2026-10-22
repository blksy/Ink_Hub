from django.test import TestCase
from artists.models import ProfessionalProfile
from artists.services import create_professional_profile
from clients.models import ClientProfile
from users.models import User


class ProfessionalProfileServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

    def test_service_creates_professional_profile(self):
        professional = create_professional_profile(self.user)

        professional_id = professional.pk

        self.assertTrue(ProfessionalProfile.objects.filter(pk=professional_id).exists())

        self.assertEqual(professional.user, self.user)

    def test_service_does_not_create_duplicate_profile(self):
        profile_1 = create_professional_profile(self.user)
        profile_2 = create_professional_profile(self.user)

        self.assertEqual(profile_1.pk, profile_2.pk)

        self.assertEqual(ProfessionalProfile.objects.filter(user=self.user).count(),1)

    def test_service_preserves_client_profile_and_role(self):
        client_profile = ClientProfile.objects.create(user=self.user)

        professional = create_professional_profile(self.user)

        self.assertEqual(professional.user, self.user)

        self.assertTrue(ClientProfile.objects.filter(user=self.user).exists())

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, User.Role.CLIENT) 

        self.assertTrue(ClientProfile.objects.filter(pk=client_profile.pk).exists())
