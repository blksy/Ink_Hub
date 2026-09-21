from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.forms import ProfessionalProfileForm, PortfolioItemForm
from artists.models import ProfessionalProfile, TattooStyle, PortfolioItem

User = get_user_model()

class ProfessionalProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="formartist@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Test Style",
            slug="test-style",
        )

    def test_form_is_valid_with_correct_data(self):
        form = ProfessionalProfileForm(
            data={
                "studio_name": "Black Moon Tattoo",
                "bio": "Tattoo artist from Poznań.",
                "location": "Poznań",
                "styles": [self.style.pk],
            },
            instance=self.professional,
        )

        self.assertTrue(form.is_valid())

    def test_form_does_not_expose_user_field(self):
        form = ProfessionalProfileForm(
            instance=self.professional
        )

        self.assertNotIn("user", form.fields)

    def test_form_contains_expected_fields(self):
        form = ProfessionalProfileForm(
            instance=self.professional
        )

        self.assertEqual(
            set(form.fields.keys()),
            {
                "studio_name",
                "bio",
                "location",
                "profile_image",
                "styles",
            },
        )


class PortfolioItemFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolio-form@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-form-test",
        )

    def test_form_contains_expected_fields(self):
        form = PortfolioItemForm()

        self.assertEqual(
            set(form.fields.keys()),
            {
                "title",
                "description",
                "image",
                "styles",
            },
        )

    def test_form_does_not_expose_professional_profile(self):
        form = PortfolioItemForm()

        self.assertNotIn(
            "professional_profile",
            form.fields,
        )