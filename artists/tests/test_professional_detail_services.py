from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, Service
from studios.models import (
    EmployeeService,
    Studio,
    StudioMembership,
)


User = get_user_model()


class ProfessionalDetailServiceTests(TestCase):
    def setUp(self):
        self.professional_user = User.objects.create_user(
            email="professional@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
        )

        self.studio = Studio.objects.create(
            name="Test Studio",
            location="Poznań",
        )

        self.category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.studio.categories.add(self.category)

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.professional,
            role=StudioMembership.Role.OWNER,
        )

        self.active_service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Active tattoo service",
            price="300.00",
            is_active=True,
        )

        self.inactive_service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Inactive tattoo service",
            price="500.00",
            is_active=False,
        )

        self.active_employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.active_service,
            price="300.00",
            duration_minutes=60,
            is_active=True,
        )

        self.inactive_employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.inactive_service,
            price="500.00",
            duration_minutes=90,
            is_active=True,
        )

        self.url = reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.professional.pk},
        )

    def test_detail_view_displays_active_service(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Active tattoo service",
        )

    def test_detail_view_does_not_display_inactive_service(self):
        response = self.client.get(self.url)

        self.assertNotContains(
            response,
            "Inactive tattoo service",
        )

    def test_services_context_contains_only_active_services(self):
        response = self.client.get(self.url)

        employee_services = response.context["employee_services"]

        self.assertIn(
            self.active_employee_service,
            employee_services,
        )

        self.assertNotIn(
            self.inactive_employee_service,
            employee_services,
        )

    def test_owner_can_see_inactive_service(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        employee_services = response.context["employee_services"]

        self.assertIn(
            self.active_employee_service,
            employee_services,
        )
        self.assertIn(
            self.inactive_employee_service,
            employee_services,
        )

    def test_public_cannot_see_inactive_employee_service(self):
        self.active_employee_service.is_active = False
        self.active_employee_service.save()

        response = self.client.get(self.url)

        employee_services = response.context["employee_services"]

        self.assertNotIn(
            self.active_employee_service,
            employee_services,
        )