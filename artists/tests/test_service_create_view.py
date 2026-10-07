from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, Service
from studios.models import Studio, StudioMembership


User = get_user_model()


class ServiceCreateViewTests(TestCase):
    def setUp(self):
        self.professional_user = User.objects.create_user(
            email="professional@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
            studio_name="Test Studio",
        )

        self.studio = Studio.objects.create(
            name="Test Studio",
            location="Poznań",
        )

        self.tattoo = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.nails = Category.objects.create(
            name="Nails",
            slug="nails",
        )

        self.studio.categories.add(self.tattoo)

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.professional,
            role=StudioMembership.Role.OWNER,
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.url = reverse(
            "professionals:service-create",
            kwargs={"studio_pk": self.studio.pk},
        )

    def test_professional_can_access_service_create_view(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "professionals/service_form.html",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_access_service_create_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_manager_can_access_service_create_view(self):
        self.membership.role = StudioMembership.Role.MANAGER
        self.membership.save()

        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_service_create_view(self):
        self.membership.role = StudioMembership.Role.EMPLOYEE
        self.membership.save()

        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_without_membership_cannot_access_service_create_view(self):
        self.membership.delete()

        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_inactive_member_cannot_access_service_create_view(self):
        self.membership.status = StudioMembership.Status.INACTIVE
        self.membership.save()

        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_can_create_service(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "category": self.tattoo.pk,
                "name": "Small tattoo",
                "description": "Small tattoo session.",
                "price": "300.00",
                "duration_minutes": "60",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Service.objects.count(), 1)

        service = Service.objects.get()

        self.assertEqual(
            service.studio,
            self.studio,
        )
        self.assertEqual(service.category, self.tattoo)
        self.assertEqual(service.name, "Small tattoo")
        self.assertTrue(service.is_active)

    def test_cannot_create_service_with_category_not_assigned_to_studio(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "category": self.nails.pk,
                "name": "Manicure",
                "description": "",
                "price": "150.00",
                "duration_minutes": "60",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.count(), 0)
        self.assertIn("category", response.context["form"].errors)
