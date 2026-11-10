from io import BytesIO
import random
import tempfile
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from clients.forms import ClientProfileForm
from clients.models import ClientProfile
from users.models import User

def create_test_image(name="test.png", size=(100, 100)):
    buffer = BytesIO()

    image = Image.new("RGB", size, color="blue")
    image.save(buffer, format="PNG")

    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type="image/png",
    )


class ClientProfileFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temp_media = tempfile.TemporaryDirectory()

        cls._media_override = override_settings(
            MEDIA_ROOT=cls._temp_media.name
        )

        cls._media_override.enable()

        try:
            super().setUpClass()
        except Exception:
            cls._media_override.disable()
            cls._temp_media.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            super().tearDownClass()
        finally:
            cls._media_override.disable()
            cls._temp_media.cleanup()

     
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

    def test_form_does_not_expose_sensitive_user_fields(self):
        form = ClientProfileForm(instance=self.client_profile)

        forbidden_fields = (
            "email",
            "role",
            "password",
            "is_staff",
            "is_superuser",
            "user_permissions",
            "groups",
        )

        for field in forbidden_fields:
            with self.subTest(field=field):
                self.assertNotIn(field, form.fields)

    def test_rejects_profile_image_larger_than_5mb(self):
        image = SimpleUploadedFile(
            "large_image.jpg",
            b"x" * (6 * 1024 * 1024),
            content_type="image/jpeg",
        )

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
            },
            files={"profile_image": image},
            instance=self.client_profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)

    def test_rejects_valid_image_larger_than_5mb(self):
        rng = random.Random(42)

        width, height = 2000, 2000

        pixels = rng.randbytes(width * height * 3)

        image = Image.frombytes("RGB", (width, height), pixels)

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        uploaded_image = SimpleUploadedFile(
            "large_image.png",
            buffer.getvalue(),
            content_type="image/png",
        )

        self.assertGreater(
            uploaded_image.size,
            5 * 1024 * 1024,
        )

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
           },
            files={"profile_image": uploaded_image},
            instance=self.client_profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)
        self.assertIn(
            "Plik nie może przekraczać 5 MB.",
            str(form.errors["profile_image"]),
        )

    def test_can_upload_profile_image(self):
        image = create_test_image()

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
            },
            files={"profile_image": image},
            instance=self.client_profile,
        )

        self.assertTrue(form.is_valid(), form.errors)

        profile = form.save()

        self.assertTrue(profile.profile_image.name)
        self.assertTrue(
            profile.profile_image.name.startswith(
                "clients/profile_images/"
            )
        )

    def test_can_clear_profile_image(self):
        self.client_profile.profile_image = "clients/profile_images/old.png"
        self.client_profile.save()

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
                "profile_image-clear": "on",
            },
            instance=self.client_profile,
        )

        self.assertTrue(form.is_valid(), form.errors)

        profile = form.save()
        profile.refresh_from_db()

        self.assertFalse(profile.profile_image)

    def test_rejects_gif_profile_image(self):
        buffer = BytesIO()

        image = Image.new("RGB", (100, 100), color="red")
        image.save(buffer, format="GIF")

        uploaded_image = SimpleUploadedFile(
            "avatar.gif",
            buffer.getvalue(),
            content_type="image/gif",
        )

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
            },
            files={"profile_image": uploaded_image},
            instance=self.client_profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)
        self.assertIn(
            "Dozwolone formaty zdjęć: JPEG, PNG, WebP.",
            str(form.errors["profile_image"]),
        )

    def test_can_replace_profile_image(self):
        old_image = create_test_image("old.png")

        self.client_profile.profile_image = old_image
        self.client_profile.save()

        old_image_name = self.client_profile.profile_image.name

        new_image = create_test_image("new.png")

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Kowalski",
                "phone_number": "123456789",
            },
            files={"profile_image": new_image},
            instance=self.client_profile,
        )

        self.assertTrue(form.is_valid(), form.errors)

        form.save() 
        self.client_profile.refresh_from_db()

        self.assertNotEqual(
            self.client_profile.profile_image.name,
            old_image_name,
        )

        self.assertTrue(
            self.client_profile.profile_image.name.endswith("new.png")
        )

    def test_invalid_image_does_not_update_profile_data(self):
        buffer = BytesIO()

        image = Image.new("RGB", (100, 100), color="red")
        image.save(buffer, format="GIF")

        uploaded_image = SimpleUploadedFile(
            "avatar.gif",
            buffer.getvalue(),
            content_type="image/gif",
        )

        form = ClientProfileForm(
            data={
                "first_name": "Adam",
                "last_name": "Nowak",
                "phone_number": "987654321",
            },
            files={"profile_image": uploaded_image},
            instance=self.client_profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)

        self.user.refresh_from_db()
        self.client_profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Jan")
        self.assertEqual(self.user.last_name, "Kowalski")
        self.assertEqual(self.client_profile.phone_number, "123456789")
        self.assertFalse(self.client_profile.profile_image)