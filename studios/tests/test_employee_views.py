from django.test import TestCase
from django.urls import reverse

from artists.models import ProfessionalProfile
from studios.models import Studio, StudioMembership
from users.models import User


class StudioEmployeeListViewTests(TestCase):

    def setUp(self):
        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )
        
        self.owner_user = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        self.owner_profile = ProfessionalProfile.objects.create(
            user=self.owner_user,
        )

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner_profile,
            role=StudioMembership.Role.OWNER,
            status = StudioMembership.Status.ACTIVE,
        )

        self.client.force_login(self.owner_user)

        self.url = reverse(
           "studios:studio-employee-list",
            kwargs={"studio_pk": self.studio.pk}, 
        )

    def test_owner_can_view_employee_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "studios/studio_employee_list.html",
        )

        self.assertContains(response, "owner@example.com")

    def test_employee_cannot_view_employee_list(self):
        self.membership.role = StudioMembership.Role.EMPLOYEE

        self.membership.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_manager_can_view_employee_list(self):
        self.membership.role = StudioMembership.Role.MANAGER

        self.membership.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "studios/studio_employee_list.html",
        )

        self.assertContains(response, "owner@example.com")

    def test_outsider_cannot_view_employee_list(self):
        outsider_user = User.objects.create_user(
            email="outsider@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        ProfessionalProfile.objects.create(user=outsider_user)

        self.client.force_login(outsider_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_client_cannot_view_employee_list(self):
        client_user = User.objects.create_user(
            email="client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )
        self.client.force_login(client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_view_employee_list(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)