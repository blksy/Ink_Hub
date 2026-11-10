from django.test import TestCase

from artists.models import ProfessionalProfile
from clients.models import ClientProfile
from clients.services import create_client_profile
from users.models import User


class ClientProfileServiceTests(TestCase):
    
    def test_service_creates_client_profile(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        client_profile = create_client_profile(user=self.user)

        self.assertTrue(ClientProfile.objects.filter(pk=client_profile.id).exists())

        self.assertEqual(client_profile.user, self.user)
 
    
    def test_service_does_not_create_duplicate_profile(self):	
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
        )

        client_profile = create_client_profile(self.user)
        client_profile2 = create_client_profile(self.user)

        self.assertEqual(client_profile, client_profile2)

        self.assertEqual(ClientProfile.objects.filter(user=self.user).count(),1) 

    def test_service_preserves_professional_profile_and_role(self):

        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        professional_profile = ProfessionalProfile.objects.create(
            user = self.user
        )

        client_profile = create_client_profile(self.user)

        self.assertTrue(ProfessionalProfile.objects.filter(pk=professional_profile.id).exists())

        self.assertTrue(ClientProfile.objects.filter(pk=client_profile.pk).exists())

        self.assertEqual(client_profile.user, self.user)

        self.user.refresh_from_db()
        
        self.assertEqual(self.user.role, User.Role.PROFESSIONAL)
