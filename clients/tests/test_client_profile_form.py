from unittest.mock import patch

from django.test import TestCase

from clients.forms import ClientProfileForm
from clients.models import ClientProfile
from users.models import User


class ClientProfileFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="jan@example.com",
            password="TestPassword123!",
            first_name="Jan",
            last_name="Kowalski",
            role=User.Role.CLIENT,
        )

        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            phone_number="123456789",
        )

    def test_form_initializes_user_fields(self):
        form = ClientProfileForm(instance=self.client_profile)

        self.assertEqual(
            form.fields["first_name"].initial,
            "Jan",
        )

        self.assertEqual(
            form.fields["last_name"].initial,
            "Kowalski",
        )

    def test_form_updates_user_and_client_profile(self):
        form_data = {
            "first_name": "Adam",
            "last_name": "Nowak",
            "phone_number": "987654321"
        }

        form = ClientProfileForm(
            data=form_data,
            instance=self.client_profile
        )

        self.assertTrue(form.is_valid(), form.errors)

        form.save()

        self.user.refresh_from_db()
        self.client_profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Adam")
        self.assertEqual(self.user.last_name, "Nowak")
        self.assertEqual(self.client_profile.phone_number, "987654321")

    def test_form_commit_false_does_not_save_to_database(self):
        form_data = {
            "first_name": "Adam",
            "last_name": "Nowak",
            "phone_number": "987654321"
        }

        form = ClientProfileForm(
            data=form_data,
            instance=self.client_profile
        )

        self.assertTrue(form.is_valid(), form.errors)

        client_profile = form.save(commit=False)

        self.assertEqual(client_profile.phone_number, "987654321")

        self.user.refresh_from_db()
        self.client_profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Jan")
        self.assertEqual(self.user.last_name, "Kowalski")
        self.assertEqual(self.client_profile.phone_number, "123456789")

    def test_form_rolls_back_transaction_on_profile_save_error(self):
        form_data = {
            "first_name": "Adam",
            "last_name": "Nowak",
            "phone_number": "987654321"
        }

        form = ClientProfileForm(
            data=form_data,
            instance=self.client_profile
        )
        
        self.assertTrue(form.is_valid(), form.errors)

        with patch.object(
            ClientProfile,
            "save",
            side_effect=Exception("Symulowany błąd"),
        ):
            with self.assertRaises(Exception):
                form.save()

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Jan")
        self.assertEqual(self.user.last_name, "Kowalski")

    def test_form_rejects_empty_first_name(self):
        form_data = {
            "first_name": "",
            "last_name": "Nowak",
            "phone_number": "987654321"
        }
        
        form = ClientProfileForm(
            data=form_data,
            instance=self.client_profile
        )

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)