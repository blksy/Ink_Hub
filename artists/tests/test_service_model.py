from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from artists.models import Category, ProfessionalProfile, Service


User = get_user_model()


class ServiceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="service@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Beauty Studio",
            location="Poznań",
        )

        self.category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        self.other_category = Category.objects.create(
            name="Nails",
            slug="nails",
        )

        self.profile.categories.add(self.category)

    def test_service_can_be_created(self):
        service = Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Haircut",
            price=Decimal("300.00"),
            duration_minutes=60,
    )

        self.assertEqual(service.name, "Haircut")
        self.assertEqual(service.price, Decimal("300.00"))
        self.assertEqual(service.duration_minutes, 60)
        self.assertEqual(service.professional, self.profile)
        self.assertEqual(service.category, self.category)

    def test_service_string_representation(self):
        service = Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Full-day tattoo session",
            price=Decimal("1800.00"),
    )

        self.assertEqual(str(service), "Full-day tattoo session")

    def test_service_is_active_by_default(self):
        service = Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Small tattoo",
            price=Decimal("300.00"),
    )

        self.assertTrue(service.is_active)

    def test_service_duration_is_optional(self):
        service = Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Tattoo consultation",
            price=Decimal("100.00"),
    )

        self.assertIsNone(service.duration_minutes)

    def test_service_category_must_belong_to_professional(self):
        service = Service(
            professional=self.profile,
            category=self.other_category,
            name="Ear piercing",
            price=Decimal("150.00"),
    )

        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_services_are_deleted_with_professional_profile(self):
        Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Small tattoo",
            price=Decimal("300.00"),
    )

        self.profile.delete()

        self.assertEqual(Service.objects.count(), 0)

    def test_category_used_by_service_cannot_be_deleted(self):
        Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Small tattoo",
            price=Decimal("300.00"),
    )

        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_professional_can_have_multiple_services(self):
        Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Small tattoo",
            price=Decimal("300.00"),
    )

        Service.objects.create(
            professional=self.profile,
            category=self.category,
            name="Full-day session",
            price=Decimal("1800.00"),
    )

        self.assertEqual(self.profile.services.count(), 2)

    def test_service_price_must_be_greater_than_zero(self):
        service = Service(
            professional=self.profile,
            category=self.category,
            name="Test service",
            price=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_service_price_cannot_be_negative(self):
        service = Service(
            professional=self.profile,
            category=self.category,
            name="Test service",
            price=Decimal("-10.00"),
        )

        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_service_duration_must_be_greater_than_zero(self):
        service = Service(
            professional=self.profile,
            category=self.category,
            name="Test service",
            price=Decimal("100.00"),
            duration_minutes=0,
        )

        with self.assertRaises(ValidationError):
            service.full_clean()

    def test_service_duration_can_be_empty(self):
        service = Service(
            professional=self.profile,
            category=self.category,
            name="Test service",
            price=Decimal("100.00"),
            duration_minutes=None,
        )

        service.full_clean()