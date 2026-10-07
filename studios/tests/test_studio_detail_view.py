from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, Service
from studios.models import Studio, StudioMembership
from users.models import User


class StudioDetailViewTests(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.owner = ProfessionalProfile.objects.create(
            user=self.owner_user,
        )

        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            description="Professional barber studio",
            location="Poznań",
        )

        self.category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        self.studio.categories.add(self.category)

        self.owner_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner,
            role=StudioMembership.Role.OWNER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.active_service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Haircut",
            price="80.00",
            duration_minutes=45,
            is_active=True,
        )

        self.inactive_service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Old service",
            price="50.00",
            duration_minutes=30,
            is_active=False,
        )

        self.url = reverse(
            "studios:studio-detail",
            kwargs={"pk": self.studio.pk},
        )

    def test_studio_detail_view_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "studios/studio_detail.html",
        )

    def test_detail_context_contains_active_service(self):
        response = self.client.get(self.url)

        services = response.context["services"]

        self.assertIn(
            self.active_service,
            services,
        )

    def test_detail_context_does_not_contain_inactive_service(self):
        response = self.client.get(self.url)

        services = response.context["services"]

        self.assertNotIn(
            self.inactive_service,
            services,
        )

    def test_detail_context_contains_active_membership(self):
        response = self.client.get(self.url)

        memberships = response.context["memberships"]

        self.assertIn(
            self.owner_membership,
            memberships,
        )

    def test_owner_can_manage_studio(self):
        self.client.force_login(self.owner_user)

        response = self.client.get(self.url)

        self.assertTrue(
            response.context["can_manage_studio"]
        )

    def test_employee_cannot_manage_studio(self):
        employee_user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        employee = ProfessionalProfile.objects.create(
            user=employee_user,
        )

        StudioMembership.objects.create(
            studio=self.studio,
            professional=employee,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        self.client.force_login(employee_user)

        response = self.client.get(self.url)

        self.assertFalse(
            response.context["can_manage_studio"]
        )

    def test_inactive_membership_is_not_displayed(self):
        self.owner_membership.status = (
            StudioMembership.Status.INACTIVE
        )
        self.owner_membership.save()

        response = self.client.get(self.url)

        memberships = response.context["memberships"]

        self.assertNotIn(
            self.owner_membership,
            memberships,
        )

