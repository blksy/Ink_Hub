from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from availability.models import WorkingHours
from studios.models import Studio, StudioMembership
from artists.models import ProfessionalProfile
from users.models import User

class WorkingHoursModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="employee@example.com",
            role=User.Role.PROFESSIONAL,
        )
        cls.profile = ProfessionalProfile.objects.create(user=cls.user)
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

    def test_can_create_working_hours(self):
        working_hours = WorkingHours(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(15, 0),
        )

        working_hours.full_clean()
        working_hours.save()

        self.assertEqual(
           WorkingHours.objects.count(),
            1,
        )

    def test_end_time_must_be_after_start_time(self):
        working_hours = WorkingHours(
            membership=self.membership,
            weekday=0,
            start_time=time(15,0),
            end_time=time(9,0),
        )

        with self.assertRaises(ValidationError)  as context:
            working_hours.full_clean()

        self.assertIn(
            "end_time",
            context.exception.message_dict,
        )

    def test_weekday_must_be_valid(self):
        working_hours = WorkingHours(
            membership=self.membership,
            weekday=7,
            start_time=time(9,0),
            end_time=time(15,0),
        )

        with self.assertRaises(ValidationError) as context:
            working_hours.full_clean()

        self.assertIn(
            "weekday",
            context.exception.message_dict,
        )

    def test_overlapping_hours_are_rejected(self):
        working_hour1 = WorkingHours.objects.create(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(13, 0),
        )

        working_hour2 = WorkingHours(
            membership=self.membership,
            weekday=0,
            start_time=time(12, 0),
            end_time=time(16, 0),
        )

        with self.assertRaises(ValidationError) as context:
            working_hour2.full_clean()

        self.assertIn(
            "start_time",
            context.exception.message_dict,
        )

        self.assertEqual(
           WorkingHours.objects.count(),
            1,
        )

    def test_adjacent_hours_are_allowed(self):
        working_hour1 = WorkingHours.objects.create(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(13, 0),
        )
        
        working_hour2 = WorkingHours(
           membership=self.membership,
           weekday=0,
           start_time=time(13, 0),
           end_time=time(16, 0),
        )
        
        working_hour2.full_clean()
        working_hour2.save()

        self.assertEqual(
            WorkingHours.objects.count(),
            2,
        )

    def test_inactive_hours_do_not_block_new_intervals(self):
        working_hour1 = WorkingHours.objects.create(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(13, 0),
            is_active=False,
        )
                
        working_hour2 = WorkingHours(
            membership=self.membership,
            weekday=0,
            start_time=time(10, 0),
            end_time=time(12, 0),
            is_active=True,
        )

        working_hour2.full_clean()
        working_hour2.save()

        self.assertEqual(
            WorkingHours.objects.count(),
            2,
        )

        self.assertFalse(working_hour1.is_active)

        self.assertTrue(working_hour2.is_active)

    def test_editing_existing_hours_does_not_conflict_with_itself(self):
        working_hour = WorkingHours.objects.create(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(13, 0),
        )

        working_hour.end_time = time(15, 0)

        working_hour.full_clean()
        working_hour.save()

        self.assertEqual(
            WorkingHours.objects.count(),
            1,
        )

        working_hour.refresh_from_db()

        self.assertEqual(
            working_hour.end_time,
            time(15, 0),
        )

    def test_different_memberships_can_have_same_hours(self):
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

        working_hour1 = WorkingHours(
            membership=self.membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(15, 0),
        )
    
        working_hour1.full_clean()
        working_hour1.save()

        working_hour2 = WorkingHours(
            membership=second_membership,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(15, 0),
        )

        working_hour2.full_clean()
        working_hour2.save()

        self.assertEqual(
            WorkingHours.objects.count(),
            2,
        )

        self.assertNotEqual(
            working_hour1.membership_id,
            working_hour2.membership_id,
        )

        self.assertEqual(
            working_hour1.membership.studio_id,
            working_hour2.membership.studio_id,
        )
