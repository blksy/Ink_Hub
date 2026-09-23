from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.forms import ServiceForm
from artists.models import Category, ProfessionalProfile


User = get_user_model()


class ServiceFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="serviceform@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Dark Ink Studio",
        )

        self.tattoo = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.piercing = Category.objects.create(
            name="Piercing",
            slug="piercing",
        )

        self.nails = Category.objects.create(
            name="Nails",
            slug="nails",
        )

        self.profile.categories.add(
            self.tattoo,
            self.piercing,
        )

    def test_form_contains_expected_fields(self):
        form = ServiceForm(professional=self.profile)

        self.assertEqual(
            set(form.fields.keys()),
            {
                "category",
                "name",
                "description",
                "price",
                "duration_minutes",
                "is_active",
            },
    )

    def test_form_only_displays_professional_categories(self):
        form = ServiceForm(professional=self.profile)

        categories = form.fields["category"].queryset

        self.assertIn(self.tattoo, categories)
        self.assertIn(self.piercing, categories)
        self.assertNotIn(self.nails, categories)

    def test_form_accepts_valid_service_data(self):
        form = ServiceForm(
            data={
                "category": self.tattoo.pk,
                "name": "Small tattoo",
                "description": "Small tattoo session.",
                "price": "300.00",
                "duration_minutes": "60",
                "is_active": True,
            },
            professional=self.profile,
    )

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_category_not_assigned_to_professional(self):
        form = ServiceForm(
            data={
                "category": self.nails.pk,
                "name": "Manicure",
                "price": "150.00",
                "duration_minutes": "60",
                "is_active": True,
            },
            professional=self.profile,
    )

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_form_has_no_categories_without_professional(self):
        form = ServiceForm()

        self.assertFalse(
            form.fields["category"].queryset.exists()
    )