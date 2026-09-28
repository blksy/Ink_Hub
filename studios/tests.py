from django.test import TestCase
from artists.models import ProfessionalProfile
from studios.models import Studio, StudioMembership
from django.db import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class StudioModelTests(TestCase):
    def test_studio_string_representation_returns_name(self):
        studio = Studio.objects.create(
            name="Gentlemen Barber Poznań",
            location="Poznań",
        )

        self.assertEqual(str(studio), "Gentlemen Barber Poznań")


    def test_professional_can_be_studio_owner(self):
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )
    
        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        membership = StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.OWNER,
        )

        self.assertEqual(membership.studio, studio)
        self.assertEqual(membership.professional, professional)
        self.assertEqual(membership.role, StudioMembership.Role.OWNER)
        self.assertEqual(
                membership.status,
            StudioMembership.Status.ACTIVE,
       )

    def test_studio_members_contains_professional(self):
        user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )

        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        self.assertIn(professional, studio.members.all())

    def test_membership_defaults_to_employee_and_active(self):
        user = User.objects.create_user(
           email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )

        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        membership = StudioMembership.objects.create(
            studio=studio,
            professional=professional,
        )

        self.assertEqual(
            membership.role,
            StudioMembership.Role.EMPLOYEE,
            )
        self.assertEqual(
            membership.status,
            StudioMembership.Status.ACTIVE,
        )

    def test_professional_cannot_have_duplicate_membership_in_same_studio(self):
        user = User.objects.create_user(
            email="employee@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        professional = ProfessionalProfile.objects.create(
            user=user,
        )
    
        studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )

        StudioMembership.objects.create(
            studio=studio,
            professional=professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        with self.assertRaises(IntegrityError):
            StudioMembership.objects.create(
                studio=studio,
                professional=professional,
                role=StudioMembership.Role.MANAGER,
        )