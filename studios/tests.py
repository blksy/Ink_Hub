from django.test import TestCase
from django.urls import reverse

from decimal import Decimal
from django.core.exceptions import ValidationError
from users.models import User
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


class StudioCreateViewTests(TestCase):
    def setUp(self):
        self.professional_user = User.objects.create_user(
            email="professional@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        self.url = reverse("studios:studio-create")

    def test_professional_can_access_studio_create_view(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "studios/studio_form.html",
        )

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_access_studio_create_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_can_create_studio(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "name": "Gentlemen Barber",
                "description": "Barbershop in Poznań",
                "location": "Poznań",
                "categories": [self.category.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        studio = Studio.objects.get(
            name="Gentlemen Barber",
        )

        self.assertEqual(
            studio.location,
            "Poznań",
        )

        self.assertIn(
            self.category,
            studio.categories.all(),
        )

    def test_creator_becomes_active_owner(self):
        self.client.force_login(self.professional_user)

        self.client.post(
            self.url,
            {
                "name": "Gentlemen Barber",
                "description": "Barbershop in Poznań",
                "location": "Poznań",
                "categories": [self.category.pk],
            },
        )

        studio = Studio.objects.get(
            name="Gentlemen Barber",
        )

        membership = StudioMembership.objects.get(
            studio=studio,
            professional=self.professional,
        )

        self.assertEqual(
            membership.role,
            StudioMembership.Role.OWNER,
        )

        self.assertEqual(
           membership.status,
            StudioMembership.Status.ACTIVE,
        )

    def test_successful_creation_redirects_to_studio_detail(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "name": "Gentlemen Barber",
                "description": "Barbershop in Poznań",
                "location": "Poznań",
                "categories": [self.category.pk],
            },
        )

        studio = Studio.objects.get(
            name="Gentlemen Barber",
        )

        self.assertRedirects(
            response,
            reverse(
                "studios:studio-detail",
                kwargs={"pk": studio.pk},
            ),
        )


class StudioUpdateViewTests(TestCase):
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
            name="Old Studio",
            location="Poznań",
        )

        self.category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        self.studio.categories.add(self.category)

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner,
            role=StudioMembership.Role.OWNER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.url = reverse(
            "studios:studio-update",
            kwargs={"studio_pk": self.studio.pk},
        )

    def test_owner_can_access_studio_update_view(self):
        self.client.force_login(self.owner_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "studios/studio_form.html",
        )

    def test_owner_can_update_studio(self):
        self.client.force_login(self.owner_user)

        response = self.client.post(
            self.url,
            {
                "name": "New Studio",
                "description": "Updated description",
                "location": "Warszawa",
                "categories": [self.category.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        self.studio.refresh_from_db()

        self.assertEqual(
            self.studio.name,
            "New Studio",
        )
        self.assertEqual(
            self.studio.location,
            "Warszawa",
        )

    def test_manager_can_access_studio_update_view(self):
        manager_user = User.objects.create_user(
            email="manager@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        manager = ProfessionalProfile.objects.create(
            user=manager_user,
        )

        StudioMembership.objects.create(
            studio=self.studio,
            professional=manager,
            role=StudioMembership.Role.MANAGER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.client.force_login(manager_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_studio_update_view(self):
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

        self.assertEqual(response.status_code, 403)

    def test_non_member_cannot_access_studio_update_view(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        ProfessionalProfile.objects.create(
            user=other_user,
        )

        self.client.force_login(other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_inactive_owner_cannot_access_studio_update_view(self):
        self.membership.status = StudioMembership.Status.INACTIVE
        self.membership.save()

        self.client.force_login(self.owner_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


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