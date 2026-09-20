from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import ArtistProfile, PortfolioItem


User = get_user_model()


class ArtistViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="viewartist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
        )

        self.profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Clover Tattoo",
            location="Poznań",
            bio="Tattoo artist from Poznań.",
        )

    def test_artist_list_view_returns_200(self):
        response = self.client.get(
            reverse("artists:artist-list")
        )

        self.assertEqual(response.status_code, 200)

    def test_artist_list_view_uses_correct_template(self):
        response = self.client.get(
            reverse("artists:artist-list")
        )

        self.assertTemplateUsed(
            response,
            "artists/artist_list.html",
        )

    def test_artist_list_contains_artist(self):
        response = self.client.get(
            reverse("artists:artist-list")
        )

        self.assertContains(
            response,
            "Black Clover Tattoo",
        )

    def test_artist_detail_view_returns_200(self):
        response = self.client.get(
            reverse(
                "artists:artist-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
    
    def test_artist_detail_displays_portfolio_item(self):
        portfolio_item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Blackwork Sleeve",
            description="Full sleeve tattoo.",
            image="artists/portfolio/test.jpg",
        )

        response = self.client.get(
            reverse(
                "artists:artist-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, portfolio_item.title)
        self.assertContains(response, portfolio_item.description)

    def test_artist_sees_portfolio_management_links_on_own_profile(self):
        portfolio_item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Blackwork Sleeve",
            image="artists/portfolio/test.jpg",
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "artists:artist-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertContains(response, "Dodaj pracę")
        self.assertContains(response, "Edytuj")
        self.assertContains(response, "Usuń")

        self.assertContains(
            response,
            reverse(
                "artists:portfolio-item-update",
                kwargs={"pk": portfolio_item.pk},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "artists:portfolio-item-delete",
                kwargs={"pk": portfolio_item.pk},
            ),
        )

    def test_other_artist_does_not_see_portfolio_management_links(self):
        portfolio_item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Blackwork Sleeve",
            image="artists/portfolio/test.jpg",
        )

        other_user = User.objects.create_user(
            email="other-viewer@example.com",
            password="InkHubTest2026!x",
            role=User.Role.ARTIST,
        )

        ArtistProfile.objects.create(
            user=other_user,
            studio_name="Other Studio",
        )

        self.client.force_login(other_user)

        response = self.client.get(
            reverse(
                "artists:artist-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertContains(response, "Blackwork Sleeve")

        self.assertNotContains(response, "Dodaj pracę")
        self.assertNotContains(response, "Edytuj")
        self.assertNotContains(response, "Usuń")

        self.assertNotContains(
            response,
            reverse(
                "artists:portfolio-item-update",
                kwargs={"pk": portfolio_item.pk},
            ),
        )
        self.assertNotContains(
            response,
            reverse(
                "artists:portfolio-item-delete",
                kwargs={"pk": portfolio_item.pk},
            ),
        )

