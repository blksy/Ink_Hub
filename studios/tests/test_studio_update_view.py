from django.test import TestCase
from django.urls import reverse

from artists.models import Category, ProfessionalProfile
from studios.models import Studio, StudioMembership
from users.models import User


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
