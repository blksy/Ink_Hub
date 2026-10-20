
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from artists.models import Category, Service
from studios.models import Studio, StudioMembership, EmployeeService
from users.models import User
from users.factories import UserFactory


class EmployeeServiceUpdateViewTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Tatuaż",
            slug="tatuaz",
        )

        self.owner = UserFactory.create_user(
            email="owner-update@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.manager = UserFactory.create_user(
            email="manager-update@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.employee = UserFactory.create_user(
            email="employee-update@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.other_employee = UserFactory.create_user(
            email="other-employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.studio = Studio.objects.create(
            name="Artiva Studio",
            location="Poznań",
        )

        self.owner_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner.professional_profile,
            role=StudioMembership.Role.OWNER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.manager_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.manager.professional_profile,
            role=StudioMembership.Role.MANAGER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.employee_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.employee.professional_profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        self.other_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.other_employee.professional_profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        self.service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Tatuaż mały",
            price=Decimal("300.00"),
            duration_minutes=60,
            is_active=True,
        )

        self.employee_service = EmployeeService.objects.create(
            membership=self.employee_membership,
            service=self.service,
            price=Decimal("350.00"),
            duration_minutes=90,
            is_active=True,
        )

        self.url = reverse(
            "studios:employee-service-update",
            kwargs={
                "studio_pk": self.studio.pk,
                "pk": self.employee_service.pk,
            },
        )

    def update_data(self):
        return {
            "price": "450.00",
            "duration_minutes": 120,
            "is_active": "on",
        }

    def test_owner_can_open_edit_form(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_manager_can_open_edit_form(self):
        self.client.force_login(self.manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_employee_can_open_own_edit_form(self):
        self.client.force_login(self.employee)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_other_employee_cannot_edit_service(self):
        self.client.force_login(self.other_employee)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_owner_can_update_employee_service(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.update_data(),
        )

        self.assertEqual(response.status_code, 302)

        self.employee_service.refresh_from_db()

        self.assertEqual(
            self.employee_service.price,
            Decimal("450.00"),
        )
        self.assertEqual(
            self.employee_service.duration_minutes,
            120,
        )

    def test_manager_can_update_employee_service(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            self.url,
            self.update_data(),
        )

        self.assertEqual(response.status_code, 302)

        self.employee_service.refresh_from_db()
        self.assertEqual(
            self.employee_service.price,
            Decimal("450.00"),
        )

    def test_employee_can_update_own_service(self):
        self.client.force_login(self.employee)

        response = self.client.post(
            self.url,
            self.update_data(),
        )

        self.assertEqual(response.status_code, 302)

        self.employee_service.refresh_from_db()
        self.assertEqual(
            self.employee_service.price,
            Decimal("450.00"),
        )

    def test_employee_cannot_change_membership_or_service(self):
        self.client.force_login(self.employee)

        original_membership = self.employee_service.membership_id
        original_service = self.employee_service.service_id

        data = self.update_data()
        data["membership"] = self.other_membership.pk
        data["service"] = 99999

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)

        self.employee_service.refresh_from_db()

        self.assertEqual(
            self.employee_service.membership_id,
            original_membership,
        )
        self.assertEqual(
            self.employee_service.service_id,
            original_service,
        )

    def test_inactive_membership_cannot_edit_service(self):
        self.employee_membership.status = StudioMembership.Status.INACTIVE
        self.employee_membership.save(update_fields=["status"])

        self.client.force_login(self.employee)

        response = self.client.get(self.url)

        self.assertIn(response.status_code, (403, 404))

    def test_can_deactivate_employee_service(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {
                "price": "350.00",
                "duration_minutes": 90,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.employee_service.refresh_from_db()
        self.assertFalse(self.employee_service.is_active)

    def test_edit_form_does_not_allow_changing_service_or_membership(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("membership", response.context["form"].fields)
        self.assertNotIn("service", response.context["form"].fields)
