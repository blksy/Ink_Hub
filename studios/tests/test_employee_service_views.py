
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, Service
from studios.models import EmployeeService, Studio, StudioMembership
from users.models import User


class EmployeeServiceViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )
        cls.employee = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )
        cls.other_owner = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        cls.owner_profile = ProfessionalProfile.objects.create(
            user=cls.owner,
        )
        cls.employee_profile = ProfessionalProfile.objects.create(
            user=cls.employee,
        )
        cls.other_profile = ProfessionalProfile.objects.create(
            user=cls.other_owner,
        )

        cls.category = Category.objects.create(
            name="Barber",
            slug="barber",
        )

        cls.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )
        cls.other_studio = Studio.objects.create(
            name="Other Barber",
            location="Warszawa",
        )

        cls.studio.categories.add(cls.category)
        cls.other_studio.categories.add(cls.category)

        cls.owner_membership = StudioMembership.objects.create(
            studio=cls.studio,
            professional=cls.owner_profile,
            role=StudioMembership.Role.OWNER,
        )
        cls.employee_membership = StudioMembership.objects.create(
            studio=cls.studio,
            professional=cls.employee_profile,
            role=StudioMembership.Role.EMPLOYEE,
        )
        cls.other_membership = StudioMembership.objects.create(
            studio=cls.other_studio,
            professional=cls.other_profile,
            role=StudioMembership.Role.OWNER,
        )

        cls.service = Service.objects.create(
            studio=cls.studio,
            category=cls.category,
            name="Strzyżenie",
            price=Decimal("80.00"),
            duration_minutes=45,
        )
        cls.other_service = Service.objects.create(
            studio=cls.other_studio,
            category=cls.category,
            name="Strzyżenie premium",
            price=Decimal("120.00"),
            duration_minutes=60,
        )

        cls.employee_service = EmployeeService.objects.create(
            membership=cls.employee_membership,
            service=cls.service,
            price=Decimal("90.00"),
            duration_minutes=50,
        )
        cls.other_employee_service = EmployeeService.objects.create(
            membership=cls.other_membership,
            service=cls.other_service,
            price=Decimal("130.00"),
            duration_minutes=60,
        )

    def detail_url(self, studio=None):
        studio = studio or self.studio
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": studio.pk},
        )

    def create_url(self):
        return reverse(
            "studios:employee-service-create",
            kwargs={"studio_pk": self.studio.pk},
        )

    def update_url(self, employee_service=None, studio=None):
        employee_service = employee_service or self.employee_service
        studio = studio or self.studio

        return reverse(
            "studios:employee-service-update",
            kwargs={
                "studio_pk": studio.pk,
                "pk": employee_service.pk,
            },
        )

    def test_guest_cannot_see_inactive_catalog_service(self):
        self.service.is_active = False
        self.service.save(update_fields=["is_active"])

        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            self.employee_service,
            response.context["employee_services"],
        )

    def test_guest_cannot_see_inactive_employee_service(self):
        self.employee_service.is_active = False
        self.employee_service.save(update_fields=["is_active"])

        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            self.employee_service,
            response.context["employee_services"],
        )

    def test_employee_can_see_own_inactive_service(self):
        self.employee_service.is_active = False
        self.employee_service.save(update_fields=["is_active"])

        self.client.force_login(self.employee)
        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.employee_service,
            response.context["employee_services"],
        )

    def test_employee_cannot_edit_other_members_service(self):
        owner_service = EmployeeService.objects.create(
            membership=self.owner_membership,
            service=self.service,
            price=Decimal("100.00"),
            duration_minutes=60,
        )

        self.client.force_login(self.employee)

        response = self.client.post(
            self.update_url(employee_service=owner_service),
            {
                "price": "999.00",
                "duration_minutes": 120,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 404)

        owner_service.refresh_from_db()

        self.assertEqual(
            owner_service.price,
            Decimal("100.00"),
        )

    def test_owner_can_edit_employee_service(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.update_url(),
            {
                "price": "150.00",
                "duration_minutes": 75,
                "is_active": "on",
            },
        )

        self.assertRedirects(
            response,
            self.detail_url(),
        )

        self.employee_service.refresh_from_db()

        self.assertEqual(
            self.employee_service.price,
            Decimal("150.00"),
        )
        self.assertEqual(
            self.employee_service.duration_minutes,
            75,
        )

    def test_owner_cannot_edit_service_from_another_studio(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.update_url(
                employee_service=self.other_employee_service,
            ),
            {
                "price": "999.00",
                "duration_minutes": 120,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 404)

        self.other_employee_service.refresh_from_db()

        self.assertEqual(
            self.other_employee_service.price,
            Decimal("130.00"),
        )

    def test_duplicate_employee_service_returns_form_error(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.create_url(),
            {
                "membership": self.employee_membership.pk,
                "service": self.service.pk,
                "price": "100.00",
                "duration_minutes": 60,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            response.context["form"].errors
        )

        self.assertEqual(
            EmployeeService.objects.filter(
                membership=self.employee_membership,
                service=self.service,
            ).count(),
            1,
        )

    def test_employee_cannot_change_service_assignment(self):
        self.client.force_login(self.employee)

        response = self.client.post(
            self.update_url(),
            {
                "membership": self.owner_membership.pk,
                "service": self.other_service.pk,
                "price": "110.00",
                "duration_minutes": 60,
                "is_active": "on",
            },
        )

        self.assertRedirects(
            response,
            self.detail_url(),
        )

        self.employee_service.refresh_from_db()

        self.assertEqual(
            self.employee_service.membership,
            self.employee_membership,
        )
        self.assertEqual(
            self.employee_service.service,
            self.service,
        )
