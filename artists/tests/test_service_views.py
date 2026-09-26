from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, Service


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

        self.tattoo = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.nails = Category.objects.create(
            name="Nails",
            slug="nails",
        )

        self.professional.categories.add(self.tattoo)

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.url = reverse("professionals:service-create")

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
            service.professional,
            self.professional,
        )
        self.assertEqual(service.category, self.tattoo)
        self.assertEqual(service.name, "Small tattoo")
        self.assertTrue(service.is_active)

    def test_professional_cannot_create_service_with_unassigned_category(self):
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


class ServiceUpdateViewTests(TestCase):
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

        self.category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.professional.categories.add(self.category)

        self.service = Service.objects.create(
            professional=self.professional,
            category=self.category,
            name="Small tattoo",
            price="300.00",
            duration_minutes=60,
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        # Drugi profesjonalista
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.other_professional = ProfessionalProfile.objects.create(
            user=self.other_user,
            studio_name="Other Studio",
        )

        self.other_professional.categories.add(self.category)

        self.url = reverse(
            "professionals:service-update",
            kwargs={"pk": self.service.pk},
        )

    def test_owner_can_access_service_update_view(self):
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

    def test_client_cannot_access_service_update_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_other_professional_cannot_edit_service(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_owner_can_update_service(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "category": self.category.pk,
                "name": "Large tattoo",
                "description": "Updated description",
                "price": "500.00",
                "duration_minutes": "120",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.service.refresh_from_db()

        self.assertEqual(self.service.name, "Large tattoo")
        self.assertEqual(self.service.price, Decimal("500.00"))
        self.assertEqual(self.service.duration_minutes, 120)
        self.assertEqual(
            self.service.description,
            "Updated description",
        )

    def test_owner_can_reactivate_inactive_service(self):
        self.service.is_active = False
        self.service.save()

        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            {
                "category": self.category.pk,
                "name": self.service.name,
                "description": self.service.description,
                "price": "300.00",
                "duration_minutes": "60",
                "is_active": True,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.service.refresh_from_db()

        self.assertTrue(self.service.is_active)


class ServiceDeleteViewTests(TestCase):
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

        self.category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.professional.categories.add(self.category)

        self.service = Service.objects.create(
            professional=self.professional,
            category=self.category,
            name="Small tattoo",
            price="300.00",
            duration_minutes=60,
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.other_professional = ProfessionalProfile.objects.create(
            user=self.other_user,
            studio_name="Other Studio",
        )

        self.other_professional.categories.add(self.category)

        self.url = reverse(
            "professionals:service-delete",
            kwargs={"pk": self.service.pk},
        )

    def test_owner_can_access_service_delete_view(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "professionals/service_confirm_delete.html",
        )

    def test_get_does_not_delete_service(self):
        self.client.force_login(self.professional_user)

        self.client.get(self.url)

        self.assertTrue(
            Service.objects.filter(pk=self.service.pk).exists()
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_delete_service(self):
        self.client.force_login(self.client_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Service.objects.filter(pk=self.service.pk).exists()
        )

    def test_other_professional_cannot_delete_service(self):
        self.client.force_login(self.other_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Service.objects.filter(pk=self.service.pk).exists()
        )

    def test_owner_can_delete_service(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Service.objects.filter(pk=self.service.pk).exists()
        )


class ProfessionalDetailServiceTests(TestCase):
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

        self.category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.professional.categories.add(self.category)

        self.active_service = Service.objects.create(
            professional=self.professional,
            category=self.category,
            name="Active tattoo service",
            price="300.00",
            is_active=True,
        )

        self.inactive_service = Service.objects.create(
            professional=self.professional,
            category=self.category,
            name="Inactive tattoo service",
            price="500.00",
            is_active=False,
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

        services = response.context["services"]

        self.assertIn(
            self.active_service,
            services,
        )
        self.assertNotIn(
            self.inactive_service,
            services,
        )

    def test_owner_can_see_inactive_service(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        services = response.context["services"]

        self.assertIn(
            self.active_service,
            services,
        )
        self.assertIn(
            self.inactive_service,
            services,
        )