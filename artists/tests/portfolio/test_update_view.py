from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from artists.models import ArtistProfile, PortfolioItem, TattooStyle


User = get_user_model()


class PortfolioItemUpdateViewTests(TestCase):
    def setUp(self):
        self.password = "InkHubTest2026!x"

        self.artist_user = User.objects.create_user(
            email="portfolio-update@example.com",
            password=self.password,
            role=User.Role.ARTIST,
        )

        self.artist = ArtistProfile.objects.create(
            user=self.artist_user,
            studio_name="Update Studio",
        )

        image = SimpleUploadedFile(
            name="portfolio.gif",
            content=(
                b"GIF87a\x01\x00\x01\x00\x80\x01\x00"
                b"\x00\x00\x00ccc,\x00\x00\x00\x00"
                b"\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

        self.portfolio_item = PortfolioItem.objects.create(
            artist_profile=self.artist,
            title="Old Title",
            description="Old description",
            image=image,
        )

        self.client_user = User.objects.create_user(
            email="portfolio-update-client@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )

        self.url = reverse(
            "artists:portfolio-item-update",
            kwargs={"pk": self.portfolio_item.pk},
        )

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


    def test_client_cannot_access_portfolio_update_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)


    def test_artist_can_access_own_portfolio_item(self):
        self.client.force_login(self.artist_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "artists/portfolio_item_form.html",
        )


    def test_artist_can_update_own_portfolio_item(self):
        self.client.force_login(self.artist_user)

        response = self.client.post(
            self.url,
            data={
                "title": "Updated Title",
                "description": "Updated description",
                "styles": [],
            },
        )

        self.assertEqual(response.status_code, 302)

        self.portfolio_item.refresh_from_db()

        self.assertEqual(
            self.portfolio_item.title,
            "Updated Title",
        )
        self.assertEqual(
            self.portfolio_item.description,
            "Updated description",
        )

    def test_artist_cannot_update_another_artists_portfolio_item(self):
        other_user = User.objects.create_user(
            email="other-portfolio-artist@example.com",
            password=self.password,
            role=User.Role.ARTIST,
        )

        other_artist = ArtistProfile.objects.create(
            user=other_user,
            studio_name="Other Studio",
        )

        other_item = PortfolioItem.objects.create(
            artist_profile=other_artist,
            title="Other Artist Tattoo",
            description="Should not be changed.",
        )

        url = reverse(
            "artists:portfolio-item-update",
            kwargs={"pk": other_item.pk},
        )

        self.client.force_login(self.artist_user)

        response = self.client.post(
            url,
            data={
                "title": "Hacked Title",
                "description": "Changed!",
                "styles": [],
            },
        )

        self.assertEqual(response.status_code, 404)

        other_item.refresh_from_db()

        self.assertEqual(
            other_item.title,
            "Other Artist Tattoo",
        )
        self.assertEqual(
            other_item.description,
            "Should not be changed.",
        )
