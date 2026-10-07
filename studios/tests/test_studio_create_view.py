from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile
from studios.models import Studio, StudioMembership
from users.models import User


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

