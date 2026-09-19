from django.contrib.auth import get_user_model
from django.test import TestCase

from users.forms import UserRegistrationForm


User = get_user_model()

class UserRegistrationFormTests(TestCase):
    def test_form_is_valid_with_correct_data(self):
        form = UserRegistrationForm(
            data={
                "email": "newuser@example.com",
                "role": User.Role.CLIENT,
                "password1": "InkHubTest2026!x",
                "password2": "InkHubTest2026!x",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_is_invalid_when_passwords_do_not_match(self):
        form = UserRegistrationForm(
            data={
                "email": "newuser@example.com",
                "role": User.Role.CLIENT,
                "password1": "InkHubTest2026!x",
                "password2": "DifferentPassword2026!x",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Passwords do not match.",
            form.non_field_errors(),
        )

    def test_form_rejects_weak_password(self):
        form = UserRegistrationForm(
            data={
                "email": "newuser@example.com",
                "role": User.Role.CLIENT,
                "password1": "123",
                "password2": "123",
            }
        )

        self.assertFalse(form.is_valid())

    def test_form_rejects_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com",
            password="ExistingTest2026!x",
            role=User.Role.CLIENT,
        )

        form = UserRegistrationForm(
            data={
                "email": "existing@example.com",
                "role": User.Role.CLIENT,
                "password1": "ArtivaTest2026!x",
                "password2": "ArtivaTest2026!x",
           }
       )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_requires_email(self):
        form = UserRegistrationForm(
            data={
                "email": "",
                "role": User.Role.CLIENT,
                "password1": "ArtivaTest2026!x",
                "password2": "ArtivaTest2026!x",
           }
       )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)