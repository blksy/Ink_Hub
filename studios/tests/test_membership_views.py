from django.test import TestCase
from django.urls import reverse

from users.models import User
from artists.models import ProfessionalProfile
from studios.models import Studio, StudioMembership


class StudioMembershipUpdateViewTests(TestCase):
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

        self.owner_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner_profile,
            role=StudioMembership.Role.OWNER,
            status=StudioMembership.Status.ACTIVE,
        )

        self.employee_user = User.objects.create_user(
            email="employee@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        self.employee_profile = ProfessionalProfile.objects.create(
            user=self.employee_user,
        )

        self.employee_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.employee_profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        self.client.force_login(self.owner_user)

        self.url = reverse(
            "studios:studio-membership-update",
            kwargs={
                "studio_pk": self.studio.pk,
                "pk": self.employee_membership.pk,
            },
        )

    def test_owner_can_update_employee_role(self):
        data = {
            "role": StudioMembership.Role.MANAGER,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)

        self.employee_membership.refresh_from_db()
        self.assertEqual(
            self.employee_membership.role,
            StudioMembership.Role.MANAGER,
        )
        

    def test_manager_cannot_update_employee_role(self):
        self.owner_membership.role = StudioMembership.Role.MANAGER
        self.owner_membership.save()

        self.employee_membership.refresh_from_db()

        self.assertEqual(
            self.employee_membership.role,
            StudioMembership.Role.EMPLOYEE,
        )

        data = {
            "role": StudioMembership.Role.EMPLOYEE,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 403)

    def test_owner_cannot_assign_owner_role(self):
        data = {
            "role": StudioMembership.Role.OWNER,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

        self.employee_membership.refresh_from_db()
        self.assertEqual(
            self.employee_membership.role,
            StudioMembership.Role.EMPLOYEE,
        )

    def test_owner_cannot_update_own_role(self):
        url = reverse(
            "studios:studio-membership-update",
        kwargs={
                "studio_pk": self.studio.pk,
                "pk": self.owner_membership.pk,
            },
        )

        response = self.client.post(
            url,
            {"role": StudioMembership.Role.EMPLOYEE},
        )

        self.assertEqual(response.status_code, 404)

        self.owner_membership.refresh_from_db()
        self.assertEqual(
            self.owner_membership.role,
            StudioMembership.Role.OWNER,
        )

    def test_owner_cannot_update_employee_from_another_studio(self):
        other_studio = Studio.objects.create(
            name="Second Barber Studio",
            location="Warszawa",
        )

        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        other_profile = ProfessionalProfile.objects.create(
            user=other_user,
        )

        other_membership = StudioMembership.objects.create(
            studio=other_studio,
            professional=other_profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        url = reverse(
            "studios:studio-membership-update",
            kwargs={
                "studio_pk": self.studio.pk,
                "pk": other_membership.pk,
            },
        )

        response = self.client.post(
            url,
            {"role": StudioMembership.Role.MANAGER},
        )

        self.assertEqual(response.status_code, 404)

        other_membership.refresh_from_db()
        self.assertEqual(
            other_membership.role,
            StudioMembership.Role.EMPLOYEE,
        )