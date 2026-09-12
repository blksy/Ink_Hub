from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import ArtistProfile

User = get_user_model()

class ArtistProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="artist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
        )

    def test_create_artist_profile(self):
        profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
            bio="Tattoo artist specialising in blackwork.",
            location="Poznań",
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.studio_name, "Black Needle")
        self.assertEqual(profile.location, "Poznań")

    def test_artist_profile_relationship(self):
        profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        self.assertEqual(self.user.artist_profile, profile)

    def test_user_can_have_only_one_artist_profile(self):
        ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        with self.assertRaises(ValidationError):
            ArtistProfile.objects.create(
                user=self.user,
                studio_name="Second Studio",
            )

    def test_string_representation_uses_studio_name(self):
        profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
        )

        self.assertEqual(str(profile), "Black Needle")

    def test_string_representation_uses_email_when_studio_name_is_empty(self):
        profile = ArtistProfile.objects.create(
            user=self.user,
        )

        self.assertEqual(str(profile), self.user.email)

    def test_client_cannot_have_artist_profile(self):
        client = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

        with self.assertRaises(ValidationError):
            ArtistProfile.objects.create(
                user=client,
                studio_name="Client Studio",
            )