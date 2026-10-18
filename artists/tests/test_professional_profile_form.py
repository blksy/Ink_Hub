
from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.forms import ProfessionalProfileForm
from artists.models import Category, ProfessionalProfile, TattooStyle


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
            name="Blackwork",
            slug="blackwork-form-test",
        )

        self.tattoo_category = Category.objects.create(
            name="Tatuaż",
            slug="tatuaz",
        )

        self.professional.categories.add(self.tattoo_category)

    def test_form_is_valid_with_correct_data(self):
        form = ProfessionalProfileForm(
            data={
                "bio": "Tattoo artist from Poznań.",
                "categories": [self.tattoo_category.pk],
                "styles": [self.style.pk],
            },
            instance=self.professional,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_does_not_expose_user_field(self):
        form = ProfessionalProfileForm(
            instance=self.professional,
        )

        self.assertNotIn("user", form.fields)

    def test_form_contains_expected_fields(self):
        form = ProfessionalProfileForm(
            instance=self.professional,
        )

        self.assertEqual(
            set(form.fields.keys()),
            {
                "bio",
                "profile_image",
                "categories",
                "styles",
            },
        )

    def test_professional_profile_form_can_assign_categories(self):
        category_one = self.tattoo_category

        category_two = Category.objects.create(
            name="Piercing",
            slug="piercing",
        )

        form = ProfessionalProfileForm(
            data={
                "bio": "Tattoo and piercing specialist.",
                "categories": [
                    category_one.pk,
                    category_two.pk,
                ],
                "styles": [],
            },
            instance=self.professional,
        )

        self.assertTrue(form.is_valid(), form.errors)

        professional = form.save()

        self.assertEqual(professional.categories.count(), 2)
        self.assertIn(category_one, professional.categories.all())
        self.assertIn(category_two, professional.categories.all())

    def test_form_rejects_nonexistent_category(self):
        form = ProfessionalProfileForm(
            data={
                "bio": "Test bio",
                "categories": [999999],
                "styles": [],
            },
            instance=self.professional,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("categories", form.errors)

    def test_non_tattoo_artist_cannot_edit_styles(self):
        barber = Category.objects.create(
            name="Barber",
            slug="barber",
        )

        self.professional.categories.set([barber])

        form = ProfessionalProfileForm(
            instance=self.professional,
        )

        self.assertNotIn("styles", form.fields)