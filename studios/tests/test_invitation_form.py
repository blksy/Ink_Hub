from django.test import TestCase

from studios.forms import StudioInvitationForm
from studios.models import Studio, StudioMembership, StudioInvitation
from artists.models import ProfessionalProfile
from users.models import User


class StudioInvitationFormTests(TestCase):

    def setUp(self):
        self.studio = Studio.objects.create(
            name="Gentlemen Barber",
            location="Poznań",
        )
        
        self.employee_user = User.objects.create_user(
            email="anna@example.com",
            password="TestPassword123!",
            role= User.Role.PROFESSIONAL,
        )

        self.employee = ProfessionalProfile.objects.create(
            user=self.employee_user
        )

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.employee,
            role=StudioMembership.Role.EMPLOYEE,
            status = StudioMembership.Status.ACTIVE
        )


    def test_cannot_invite_existing_active_studio_member(self):
        data ={
            "email": "anna@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }

        form = StudioInvitationForm(data=data, studio=self.studio)
        self.assertFalse(form.is_valid()) 
        self.assertIn(
            "Ten użytkownik jest już pracownikiem tego studia.",
            form.errors["email"],
        )

    def test_can_invite_new_employee(self):
        data = {
            "email": "piotr@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }

        form = StudioInvitationForm(data=data, studio=self.studio)
        self.assertTrue(form.is_valid())


    def test_cannot_invite_employee_with_pending_invitation(self):
        data = {
            "email": "piotr@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }

        StudioInvitation.objects.create(
            studio=self.studio,
            email="piotr@example.com",
            role=StudioMembership.Role.EMPLOYEE,
        )

        form = StudioInvitationForm(data=data, studio=self.studio)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        print(form.errors)

    def test_can_invite_after_previous_invitation_cancelled(self):
        data = {
            "email": "piotr@example.com",
            "role": StudioMembership.Role.EMPLOYEE,
        }
        
        StudioInvitation.objects.create(
            studio=self.studio,
            email="piotr@example.com",
            role=StudioMembership.Role.EMPLOYEE,
            status=StudioInvitation.Status.CANCELLED,
         ) 

        form = StudioInvitationForm(data=data, studio=self.studio)
        self.assertTrue(form.is_valid())

