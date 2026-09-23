from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from artists.models import ProfessionalProfile, TattooStyle


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
            studio_name="Black Needle",
            bio="Tattoo artist specialising in blackwork.",
            location="Poznań",
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.studio_name, "Black Needle")
        self.assertEqual(profile.location, "Poznań")

    def test_professional_profile_relationship(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        self.assertEqual(self.user.professional_profile, profile)

    def test_user_can_have_only_one_professional_profile(self):
        ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        with self.assertRaises(ValidationError):
            ProfessionalProfile.objects.create(
                user=self.user,
                studio_name="Second Studio",
            )

    def test_string_representation_uses_studio_name(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        self.assertEqual(str(profile), "Black Needle")

    def test_string_representation_uses_email_when_studio_name_is_empty(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.assertEqual(str(profile), self.user.email)

    def test_client_cannot_have_professional_profile(self):
        client = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        with self.assertRaises(ValidationError):
            ProfessionalProfile.objects.create(
                user=client,
                studio_name="Client Studio",
        )

    def test_professional_can_have_multiple_styles(self):
        profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
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
            studio_name="Black Needle",
    )

        second_profile = ProfessionalProfile.objects.create(
            user=second_user,
            studio_name="Second Studio",
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



    
