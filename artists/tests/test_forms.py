from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.forms import ArtistProfileForm, PortfolioItemForm
from artists.models import ArtistProfile, TattooStyle, PortfolioItem

User = get_user_model()

class ArtistProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="formartist@example.com",
            password="ArtivaTest2026!x",
            role=User.Role.ARTIST,
        )

        self.artist = ArtistProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Test Style",
            slug="test-style",
        )

    def test_form_is_valid_with_correct_data(self):
        form = ArtistProfileForm(
            data={
                "studio_name": "Black Moon Tattoo",
                "bio": "Tattoo artist from Poznań.",
                "location": "Poznań",
                "styles": [self.style.pk],
            },
            instance=self.artist,
        )

        self.assertTrue(form.is_valid())

    def test_form_does_not_expose_user_field(self):
        form = ArtistProfileForm(
            instance=self.artist
        )

        self.assertNotIn("user", form.fields)

    def test_form_contains_expected_fields(self):
        form = ArtistProfileForm(
            instance=self.artist
        )

        self.assertEqual(
            set(form.fields.keys()),
            {
                "studio_name",
                "bio",
                "location",
                "profile_image",
                "styles",
            },
        )

class PortfolioItemFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolio-form@example.com",
            password="ArtivaTest2026!x",
            role=User.Role.ARTIST,
        )

        self.artist = ArtistProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-form-test",
        )

    def test_form_contains_expected_fields(self):
        form = PortfolioItemForm()

        self.assertEqual(
            set(form.fields.keys()),
            {
                "title",
                "description",
                "image",
                "styles",
            },
        )

    def test_form_does_not_expose_artist_profile(self):
        form = PortfolioItemForm()

        self.assertNotIn(
            "artist_profile",
            form.fields,
        )