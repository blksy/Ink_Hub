from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.models import Category, ProfessionalProfile


User = get_user_model()


class CategoryModelTests(TestCase):
    def setUp(self):
        self.password = "ArtivaTest2026!x"

    def test_category_string_representation(self):
        category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.assertEqual(str(category), "Tattoo")

    def test_professional_can_have_multiple_categories(self):
        user = User.objects.create_user(
            email="professional@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
            studio_name="Dark Ink Studio",
        )

        tattoo = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        piercing = Category.objects.create(
            name="Piercing",
            slug="piercing",
        )

        professional.categories.add(tattoo, piercing)

        self.assertEqual(professional.categories.count(), 2)
        self.assertIn(tattoo, professional.categories.all())
        self.assertIn(piercing, professional.categories.all())

    def test_category_can_have_multiple_professionals(self):
        tattoo = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        user_one = User.objects.create_user(
            email="professional1@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        user_two = User.objects.create_user(
            email="professional2@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        professional_one = ProfessionalProfile.objects.create(
            user=user_one,
        )

        professional_two = ProfessionalProfile.objects.create(
            user=user_two,
        )

        professional_one.categories.add(tattoo)
        professional_two.categories.add(tattoo)

        self.assertEqual(tattoo.professionals.count(), 2)
        self.assertIn(
            professional_one,
            tattoo.professionals.all(),
        )
        self.assertIn(
            professional_two,
            tattoo.professionals.all(),
        )


