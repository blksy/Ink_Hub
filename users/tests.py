from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from artists.models import ArtistProfile
from .factories import UserFactory
from .forms import UserRegistrationForm

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
        )

        self.assertEqual(user.email, "client@example.com")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_artist_user(self):
        user = User.objects.create_user(
            email="artist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
        )

        self.assertEqual(user.role, User.Role.ARTIST)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="testpass123",
            )

    def test_email_must_be_unique(self):
        User.objects.create_user(
            email="duplicate@example.com",
            password="testpass123",
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="duplicate@example.com",
                password="anotherpass123",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_superuser_must_have_is_staff_true(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False,
            )

    def test_superuser_must_have_is_superuser_true(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_superuser=False,
            )

class UserFactoryTests(TestCase):
    def test_factory_creates_client(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.assertEqual(user.email, "client@example.com")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertTrue(
            User.objects.filter(email="client@example.com").exists()
        )

    def test_factory_does_not_create_artist_profile_for_client(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        self.assertFalse(
            ArtistProfile.objects.filter(user=user).exists()
        )

    def test_factory_creates_artist_with_profile(self):
        user = UserFactory.create_user(
            email="artist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
       )

        self.assertEqual(user.role, User.Role.ARTIST)

        self.assertTrue(
            ArtistProfile.objects.filter(user=user).exists()
       )

    def test_factory_hashes_password(self):
        user = UserFactory.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
       )

        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.check_password("testpass123"))
 
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