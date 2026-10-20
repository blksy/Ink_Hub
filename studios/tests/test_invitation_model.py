from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from studios.models import (
    Studio,
    StudioInvitation,
    StudioMembership,
)


class StudioInvitationModelTests(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        self.other_studio = Studio.objects.create(
            name="Other Studio",
            location="Poznań",
        )

        self.expires_at = (
            timezone.now() + timedelta(days=7)
        )

    def test_invitation_can_be_created(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertEqual(
            invitation.studio,
            self.studio,
        )
        self.assertEqual(
            invitation.email,
            "employee@example.com",
        )

    def test_invitation_default_status_is_pending(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertEqual(
            invitation.status,
            StudioInvitation.Status.PENDING,
        )

    def test_invitation_default_role_is_employee(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertEqual(
            invitation.role,
            StudioMembership.Role.EMPLOYEE,
        )

    def test_invitation_token_is_generated(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertIsNotNone(
            invitation.token,
        )

    def test_invitations_have_unique_tokens(self):
        first_invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="first@example.com",
            expires_at=self.expires_at,
        )

        second_invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="second@example.com",
            expires_at=self.expires_at,
        )

        self.assertNotEqual(
            first_invitation.token,
            second_invitation.token,
        )

    def test_duplicate_pending_invitation_is_not_allowed(self):
        StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudioInvitation.objects.create(
                    studio=self.studio,
                    email="employee@example.com",
                    expires_at=self.expires_at,
                )

    def test_same_email_can_have_pending_invitation_in_different_studio(self):
        StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        second_invitation = StudioInvitation.objects.create(
            studio=self.other_studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertEqual(
            second_invitation.studio,
            self.other_studio,
        )

    def test_new_pending_invitation_is_allowed_after_accepted_invitation(self):
        StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            status=StudioInvitation.Status.ACCEPTED,
            expires_at=self.expires_at,
        )

        new_invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=self.expires_at,
        )

        self.assertEqual(
            new_invitation.status,
            StudioInvitation.Status.PENDING,
        )

    def test_future_pending_invitation_is_valid(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
           expires_at=timezone.now() + timedelta(days=7),
        )

        self.assertTrue(
            invitation.is_valid()
        )

    def test_past_invitation_is_expired(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertTrue(
            invitation.is_expired()
        )

    def test_expired_pending_invitation_is_not_valid(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertFalse(
            invitation.is_valid()
        )

    def test_accepted_invitation_is_not_valid(self):
        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
            status=StudioInvitation.Status.ACCEPTED,
            expires_at=timezone.now() + timedelta(days=7),
        )

        self.assertFalse(
            invitation.is_valid()
        )

    def test_invitation_expires_after_seven_days_by_default(self):
        before_creation = timezone.now()

        invitation = StudioInvitation.objects.create(
            studio=self.studio,
            email="employee@example.com",
        )

        after_creation = timezone.now()

        self.assertGreaterEqual(
            invitation.expires_at,
            before_creation + timedelta(days=7),
        )

        self.assertLessEqual(
           invitation.expires_at,
            after_creation + timedelta(days=7),
        )