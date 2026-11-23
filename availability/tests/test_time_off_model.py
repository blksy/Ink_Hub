
from datetime import datetime, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from availability.models import TimeOff
from users.models import User
from artists.models import ProfessionalProfile
from studios.models import Studio, StudioMembership


class TimeOffModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="employee@example.com",
            role=User.Role.PROFESSIONAL,
        )

        cls.profile = ProfessionalProfile.objects.create(
            user=cls.user,
        )

        cls.studio = Studio.objects.create(
            name="Test Studio",
            location="Poznan",
        )

        cls.membership = StudioMembership.objects.create(
            studio=cls.studio,
            professional=cls.profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

    def test_can_create_time_off(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )
        end = start + timedelta(hours=2)

        time_off = TimeOff(
            membership=self.membership,
            reason="Doctor appointment",
            start_at=start,
            end_at=end,
        )

        time_off.full_clean()
        time_off.save()
        time_off.refresh_from_db()

        self.assertEqual(TimeOff.objects.count(), 1)
        self.assertEqual(time_off.start_at, start)
        self.assertEqual(time_off.end_at, end)
        self.assertEqual(time_off.reason, "Doctor appointment")
        self.assertEqual(time_off.membership_id, self.membership.pk)
        self.assertIsNotNone(time_off.created_at)

    def test_end_at_must_be_after_start_at(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 12, 0)
        )
        end = start - timedelta(hours=2)

        time_off = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=end,
        )

        with self.assertRaises(ValidationError) as context:
            time_off.full_clean()

        self.assertIn("end_at", context.exception.message_dict)
        self.assertEqual(TimeOff.objects.count(), 0)

    def test_equal_start_and_end_are_rejected(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        time_off = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start,
        )

        with self.assertRaises(ValidationError) as context:
            time_off.full_clean()

        self.assertIn("end_at", context.exception.message_dict)
        self.assertEqual(TimeOff.objects.count(), 0)

    def test_overlapping_time_off_is_rejected(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        first = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start + timedelta(hours=2),
        )

        first.full_clean()
        first.save()

        second = TimeOff(
            membership=self.membership,
            start_at=start + timedelta(hours=1),
            end_at=start + timedelta(hours=3),
        )

        with self.assertRaises(ValidationError) as context:
            second.full_clean()

        self.assertIn("start_at", context.exception.message_dict)
        self.assertEqual(TimeOff.objects.count(), 1)

    def test_adjacent_time_off_is_allowed(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        first = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start + timedelta(hours=2),
        )

        first.full_clean()
        first.save()

        second = TimeOff(
            membership=self.membership,
            start_at=first.end_at,
            end_at=first.end_at + timedelta(hours=2),
        )

        second.full_clean()
        second.save()

        self.assertEqual(TimeOff.objects.count(), 2)

    def test_editing_existing_time_off_does_not_conflict_with_itself(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        time_off = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start + timedelta(hours=2),
        )

        time_off.full_clean()
        time_off.save()

        new_end = start + timedelta(hours=4)

        time_off.end_at = new_end
        time_off.full_clean()
        time_off.save()
        time_off.refresh_from_db()

        self.assertEqual(TimeOff.objects.count(), 1)
        self.assertEqual(time_off.end_at, new_end)

    def test_different_memberships_can_have_same_time_off(self):
        second_user = User.objects.create_user(
            email="second_employee@example.com",
            role=User.Role.PROFESSIONAL,
        )

        second_profile = ProfessionalProfile.objects.create(
            user=second_user,
        )

        second_membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=second_profile,
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioMembership.Status.ACTIVE,
        )

        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )
        end = start + timedelta(hours=2)

        first = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=end,
        )

        first.full_clean()
        first.save()

        second = TimeOff(
            membership=second_membership,
            start_at=start,
            end_at=end,
        )

        second.full_clean()
        second.save()

        self.assertEqual(TimeOff.objects.count(), 2)
        self.assertNotEqual(
            first.membership_id,
            second.membership_id,
        )

    def test_multi_day_time_off_is_allowed(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 0, 0)
        )
        end = start + timedelta(days=7)

        time_off = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=end,
            reason="Vacation",
        )

        time_off.full_clean()
        time_off.save()
        time_off.refresh_from_db()

        self.assertEqual(TimeOff.objects.count(), 1)
        self.assertEqual(
            time_off.end_at - time_off.start_at,
            timedelta(days=7),
        )

    def test_time_off_inside_existing_period_is_rejected(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        first = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start + timedelta(hours=6),
        )

        first.full_clean()
        first.save()

        second = TimeOff(
            membership=self.membership,
            start_at=start + timedelta(hours=1),
            end_at=start + timedelta(hours=2),
        )

        with self.assertRaises(ValidationError) as context:
            second.full_clean()

        self.assertIn("start_at", context.exception.message_dict)
        self.assertEqual(TimeOff.objects.count(), 1)

    def test_reason_is_optional(self):
        start = timezone.make_aware(
            datetime(2026, 11, 24, 10, 0)
        )

        time_off = TimeOff(
            membership=self.membership,
            start_at=start,
            end_at=start + timedelta(hours=2),
        )

        time_off.full_clean()
        time_off.save()
        time_off.refresh_from_db()

        self.assertEqual(TimeOff.objects.count(), 1)
        self.assertEqual(time_off.reason, "")
