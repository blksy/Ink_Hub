
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from artists.models import ProfessionalProfile
from studios.models import Studio, StudioInvitation, StudioMembership
from users.models import User


class StudioInvitationAcceptRejectViewTests(TestCase):

    def setUp(self):
        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        self.user = User.objects.create_user(
            email="employee@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email=self.user.email,
            role=StudioMembership.Role.EMPLOYEE,
        )

        self.accept_url = reverse(
            "studios:invitation-accept",
            kwargs={"pk": self.invitation.pk},
        )

        self.reject_url = reverse(
            "studios:invitation-reject",
            kwargs={"pk": self.invitation.pk},
       )

        self.client.force_login(self.user)

    def test_professional_can_accept_invitation(self):
        response = self.client.post(self.accept_url)

        self.assertRedirects(
            response,
            reverse(
                "studios:studio-detail",
                kwargs={"pk": self.studio.pk},
            ),
        )

        membership = StudioMembership.objects.get(
            studio=self.studio,
            professional=self.professional,
        )

        self.assertEqual(
            membership.role,
            StudioMembership.Role.EMPLOYEE,
        )
        self.assertEqual(
            membership.status,
            StudioMembership.Status.ACTIVE,
        )

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.ACCEPTED,
        )

    def test_other_user_cannot_accept_invitation(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )
        ProfessionalProfile.objects.create(user=other_user)
        self.client.force_login(other_user)

        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_anonymous_user_cannot_accept_invitation(self):
        self.client.logout()

        response = self.client.post(self.accept_url)

        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_expired_invitation_cannot_be_accepted(self):
        self.invitation.expires_at = (
            timezone.now() - timedelta(days=1)
        )
        self.invitation.save(update_fields=["expires_at"])

        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 403)

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.EXPIRED,
        )

        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_owner_invitation_cannot_be_accepted(self):
        self.invitation.role = StudioMembership.Role.OWNER
        self.invitation.save(update_fields=["role"])

        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_accepted_invitation_cannot_be_accepted_again(self):
        self.client.post(self.accept_url)

        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).count(),
            1,
        )

    def test_inactive_membership_is_reactivated(self):
        membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.professional,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.INACTIVE,
        )

        self.invitation.role = StudioMembership.Role.MANAGER
        self.invitation.save(update_fields=["role"])

        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 302)

        membership.refresh_from_db()
        self.assertEqual(
            membership.status,
            StudioMembership.Status.ACTIVE,
        )
        self.assertEqual(
            membership.role,
            StudioMembership.Role.MANAGER,
        )

        self.assertEqual(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).count(),
            1,
        )

    def test_professional_can_reject_invitation(self):
        response = self.client.post(self.reject_url)

        self.assertRedirects(
            response,
            reverse("studios:my-invitations"),
        )

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.REJECTED,
        )

        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_other_user_cannot_reject_invitation(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPassword123!",
            role=User.Role.PROFESSIONAL,
        )
        ProfessionalProfile.objects.create(user=other_user)
        self.client.force_login(other_user)

        response = self.client.post(self.reject_url)

        self.assertEqual(response.status_code, 404)

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.PENDING,
        )

    def test_expired_invitation_is_marked_expired_on_rejection(self):
        self.invitation.expires_at = (
            timezone.now() - timedelta(days=1)
        )
        self.invitation.save(update_fields=["expires_at"])

        response = self.client.post(self.reject_url)

        self.assertEqual(response.status_code, 302)

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.EXPIRED,
        )

    def test_invitation_cannot_be_accepted_using_get(self):
        response = self.client.get(self.accept_url)

        self.assertEqual(response.status_code, 405)
        self.assertFalse(
            StudioMembership.objects.filter(
                studio=self.studio,
                professional=self.professional,
            ).exists()
        )

    def test_invitation_cannot_be_rejected_using_get(self):
        response = self.client.get(self.reject_url)

        self.assertEqual(response.status_code, 405)

        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status,
            StudioInvitation.Status.PENDING,
        )
