from django.test import TestCase
from decimal import Decimal
from django.core.exceptions import ValidationError
from artists.models import ProfessionalProfile, Category, Service
from studios.models import EmployeeService, Studio, StudioMembership
from django.db import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class StudioModelTests(TestCase):
    def test_studio_string_representation_returns_name(self):
        studio = Studio.objects.create(
            name="Gentlemen Barber Poznań",
            location="Poznań",
        )

        self.assertEqual(str(studio), "Gentlemen Barber Poznań")


    def test_professional_can_be_studio_owner(self):
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )
    
        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        membership = StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.OWNER,
        )

        self.assertEqual(membership.studio, studio)
        self.assertEqual(membership.professional, professional)
        self.assertEqual(membership.role, StudioMembership.Role.OWNER)
        self.assertEqual(
                membership.status,
            StudioMembership.Status.ACTIVE,
       )

    def test_studio_members_contains_professional(self):
        user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )

        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        self.assertIn(professional, studio.members.all())

    def test_membership_defaults_to_employee_and_active(self):
        user = User.objects.create_user(
           email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )

        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        membership = StudioMembership.objects.create(
            studio=studio,
            professional=professional,
        )

        self.assertEqual(
            membership.role,
            StudioMembership.Role.EMPLOYEE,
            )
        self.assertEqual(
            membership.status,
            StudioMembership.Status.ACTIVE,
        )

    def test_professional_cannot_have_duplicate_membership_in_same_studio(self):
        user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )
    
        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        with self.assertRaises(IntegrityError):
            StudioMembership.objects.create(
                studio=studio,
                professional=professional,
                role=StudioMembership.Role.MANAGER,
        )

    def test_studio_can_have_categories(self):
        category = Category.objects.create(
            name="Barber",
            slug="barber",
        )

        studio = Studio.objects.create(
           name="Gentlemen Barber",
            location="Poznań",
        )

        studio.categories.add(category)

        self.assertIn(
            category,
            studio.categories.all(),
        )


class EmployeeServiceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.profile = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.category = Category.objects.create(
            name="Barber",
            slug="barber",
        )

        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        self.studio.categories.add(self.category)

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.profile,
            role=StudioMembership.Role.EMPLOYEE,
        )

        self.service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Strzyżenie męskie",
            price=Decimal("80.00"),  # legacy
            duration_minutes=45,     # legacy
        )

    def test_employee_service_can_be_created(self):
        employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.service,
            price=Decimal("90.00"),
            duration_minutes=50,
        )

        self.assertEqual(
            employee_service.membership,
            self.membership,
       )
        self.assertEqual(
            employee_service.service,
            self.service,
        )
        self.assertEqual(
           employee_service.price,
            Decimal("90.00"),
        )
        self.assertEqual(
            employee_service.duration_minutes,
            50,
        )
        self.assertTrue(employee_service.is_active)

    def test_employee_service_reverse_relations(self):
        employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.service,
            price=Decimal("90.00"),
            duration_minutes=50,
        )

        self.assertIn(
            employee_service,
            self.membership.employee_services.all(),
        )
    
        self.assertIn(
            employee_service,
            self.service.employee_services.all(),
        )

    def test_service_must_belong_to_membership_studio(self):
        other_studio = Studio.objects.create(
            name="Other Studio",
            location="Poznań",
        )

        other_studio.categories.add(self.category)

        other_service = Service.objects.create(
            studio=other_studio,
            category=self.category,
            name="Other service",
            price=Decimal("100.00"),
            duration_minutes=60,
        )

        employee_service = EmployeeService(
            membership=self.membership,
            service=other_service,
            price=Decimal("100.00"),
            duration_minutes=60,
        )

        with self.assertRaises(ValidationError):
            employee_service.full_clean()

    def test_membership_cannot_have_duplicate_employee_service(self):
        EmployeeService.objects.create(
            membership=self.membership,
            service=self.service,
            price=Decimal("90.00"),
            duration_minutes=50,
        )

        with self.assertRaises(IntegrityError):
            EmployeeService.objects.create(
                membership=self.membership,
                service=self.service,
                price=Decimal("100.00"),
                duration_minutes=60,
            )

    def test_employee_service_string_representation(self):
        employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.service,
            price=Decimal("90.00"),
            duration_minutes=50,
        )

        self.assertEqual(
            str(employee_service),
            f"{self.profile} - {self.service}",
        )

    def test_employee_service_price_must_be_positive(self):
        employee_service = EmployeeService(
            membership=self.membership,
            service=self.service,
            price=Decimal("0.00"),
            duration_minutes=45,
        )

        with self.assertRaises(ValidationError):
            employee_service.full_clean()

    def test_employee_service_duration_must_be_positive(self):
        employee_service = EmployeeService(
            membership=self.membership,
            service=self.service,
            price=Decimal("80.00"),
            duration_minutes=0,
        )

        with self.assertRaises(ValidationError):
            employee_service.full_clean()

    def test_employee_service_requires_active_membership(self):
        self.membership.status = StudioMembership.Status.INACTIVE
        self.membership.save()

        employee_service = EmployeeService(
            membership=self.membership,
            service=self.service,
            price=Decimal("80.00"),
            duration_minutes=45,
        )

        with self.assertRaises(ValidationError):
            employee_service.full_clean()