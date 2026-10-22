from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from artists.models import ProfessionalProfile, TattooStyle
from clients.models import ClientProfile


User = get_user_model()


class ProfessionalProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="artist@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

    def test_create_professional_profile(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
            bio="Tattoo artist specialising in blackwork.",
        )

        self.assertEqual(profile.user, self.user)

    def test_professional_profile_relationship(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.assertEqual(self.user.professional_profile, profile)

    def test_user_can_have_only_one_professional_profile(self):
        ProfessionalProfile.objects.create(
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            ProfessionalProfile.objects.create(
                user=self.user,
            )

    def test_string_representation_uses_full_name(self):
        self.user.first_name = "Jan"
        self.user.last_name = "Kowalski"
        self.user.save()

        profile = ProfessionalProfile.objects.create(
            user=self.user,
    )

        self.assertEqual(str(profile), "Jan Kowalski")
        
    def test_string_representation_uses_email_when_full_name_name_is_empty(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.assertEqual(str(profile), self.user.email)

    def test_client_is_allowed_to_have_professional_profile(self):
        client = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        professional = ProfessionalProfile.objects.create(user = client)
        client.refresh_from_db()

        self.assertEqual(client.role, User.Role.CLIENT)

        self.assertEqual(professional.user, client)

    def test_professional_can_have_multiple_styles(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
       )

        blackwork = TattooStyle.objects.create(name="Blackwork", slug="blackwork",)
        realism = TattooStyle.objects.create(name="Realism", slug="realism",)

        profile.styles.add(blackwork, realism)

        self.assertEqual(profile.styles.count(), 2)
        self.assertIn(blackwork, profile.styles.all())
        self.assertIn(realism, profile.styles.all())


    def test_style_can_belong_to_multiple_professionals(self):
        second_user = User.objects.create_user(
            email="secondartist@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
    )

        first_profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        second_profile = ProfessionalProfile.objects.create(
            user=second_user,
        )

        blackwork = TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

        first_profile.styles.add(blackwork)
        second_profile.styles.add(blackwork)

        self.assertEqual(blackwork.professionals.count(), 2)
        self.assertIn(first_profile, blackwork.professionals.all())
        self.assertIn(second_profile, blackwork.professionals.all())


    def test_tattoo_style_name_must_be_unique(self):
        TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

        with self.assertRaises(IntegrityError):
            TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

    def test_create_tattoo_style_with_slug(self):
        style = TattooStyle.objects.create(
            name="Fine Line",
            slug="fine-line",
        )

        self.assertEqual(style.name, "Fine Line")
        self.assertEqual(style.slug, "fine-line")
        self.assertEqual(str(style), "Fine Line")

    def test_professional_profile_without_phone_number(self):
        professional  = ProfessionalProfile.objects.create(
            user=self.user
        )

        self.assertEqual(professional.phone_number, "")

    def test_user_can_have_both_profiles(self):
        professional_profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        client_profile = ClientProfile.objects.create(
            user=self.user
        )

        self.assertEqual(self.user.client_profile, client_profile)
        self.assertEqual(self.user.professional_profile, professional_profile)
        self.assertEqual(self.user.role, User.Role.PROFESSIONAL)

    def test_deleting_client_profile_preserves_professional_profile(self):
        user = self.user

        client_profile = ClientProfile.objects.create(
            user=self.user
        )

        professional_profile = ProfessionalProfile.objects.create(
            user=self.user
        )

        client_profile_id = client_profile.pk
        professional_profile_id =  professional_profile.pk

        client_profile.delete()

        self.assertTrue(ProfessionalProfile.objects.filter(pk=professional_profile_id).exists())
        self.assertFalse(ClientProfile.objects.filter(pk=client_profile_id).exists())
        self.assertTrue(User.objects.filter(pk=user.pk).exists())