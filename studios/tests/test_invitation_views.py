from django.test import TestCase
from django.urls import reverse

from studios.models import Studio, StudioInvitation, StudioMembership
from artists.models import ProfessionalProfile
from users.models import User


class StudioInvitationCreateViewTests(TestCase):

    def setUp(self):
        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        self.owner_user = User.objects.create_user(
            email="anna@example.com",
            password="TestPassword123!",
            role= User.Role.PROFESSIONAL,
        )

        self.owner = ProfessionalProfile.objects.create(
            user=self.owner_user
        )

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.owner,
            role=StudioMembership.Role.OWNER,
            status = StudioMembership.Status.ACTIVE
        )

        self.url = reverse(
            "studios:studio-invitation-create",
            kwargs={"studio_pk": self.studio.pk},
        )

        self.client.force_login(self.owner_user)

    def test_owner_can_access_invitation_form(self):
        url = reverse(
            "studios:studio-invitation-create",
            kwargs={"studio_pk": self.studio.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_access_invitation_form(self):
        self.membership.role = StudioMembership.Role.EMPLOYEE
        self.membership.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)


    def test_manager_can_access_invitation_form(self):
        self.membership.role = StudioMembership.Role.MANAGER
        self.membership.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_invitation_form(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_owner_can_create_invitation(self):
        data = {
            "email": "employee@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(StudioInvitation.objects.count(), 1)

        invitation = StudioInvitation.objects.first()

        self.assertEqual(invitation.email, "employee@example.com")
        self.assertEqual(invitation.studio, self.studio)
        self.assertEqual(
            invitation.role,
            StudioMembership.Role.EMPLOYEE,
        )

        self.assertRedirects(
            response,
            reverse(
                "studios:studio-detail",
                kwargs={"pk": self.studio.pk},
            ),
        )

    def test_cannot_create_owner_invitation(self):
        data = {
            "email": "employee@example.com",
            "role": StudioMembership.Role.OWNER,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(StudioInvitation.objects.count(), 0)

    def test_cannot_create_duplicate_pending_invitation(self):
        StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            role=StudioMembership.Role.EMPLOYEE,
        )

        data = {
            "email": "employee@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(StudioInvitation.objects.count(), 1)