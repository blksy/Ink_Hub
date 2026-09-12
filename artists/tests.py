from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import ArtistProfile, TattooStyle, PortfolioItem

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

    def test_artist_can_have_multiple_styles(self):
        profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
       )

        blackwork = TattooStyle.objects.create(name="Blackwork", slug="blackwork",)
        realism = TattooStyle.objects.create(name="Realism", slug="realism",)

        profile.styles.add(blackwork, realism)

        self.assertEqual(profile.styles.count(), 2)
        self.assertIn(blackwork, profile.styles.all())
        self.assertIn(realism, profile.styles.all())


    def test_style_can_belong_to_multiple_artists(self):
        second_user = User.objects.create_user(
            email="secondartist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
    )

        first_profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Black Needle",
    )

        second_profile = ArtistProfile.objects.create(
            user=second_user,
            studio_name="Second Studio",
    )

        blackwork = TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

        first_profile.styles.add(blackwork)
        second_profile.styles.add(blackwork)

        self.assertEqual(blackwork.artists.count(), 2)
        self.assertIn(first_profile, blackwork.artists.all())
        self.assertIn(second_profile, blackwork.artists.all())


    def test_tattoo_style_name_must_be_unique(self):
        TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

        with self.assertRaises(IntegrityError):
            TattooStyle.objects.create(name="Blackwork", slug="blackwork",)

    def test_create_tattoo_style_with_slug(self):
        style = TattooStyle.objects.create(
            name="Fine Line",
            slug="fine-line",
    )

        self.assertEqual(style.name, "Fine Line")
        self.assertEqual(style.slug, "fine-line")
        self.assertEqual(str(style), "Fine Line")

class PortfolioItemModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolioartist@example.com",
            password="testpass123",
            role=User.Role.ARTIST,
        )

        self.profile = ArtistProfile.objects.create(
            user=self.user,
            studio_name="Ink House",
        )

    def test_create_portfolio_item(self):
        item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Blackwork sleeve",
            description="Full sleeve tattoo.",
            image="artists/portfolio/test.jpg",
    )

        self.assertEqual(item.artist_profile, self.profile)
        self.assertEqual(item.title, "Blackwork sleeve")
        self.assertEqual(item.description, "Full sleeve tattoo.")

    def test_artist_can_have_multiple_portfolio_items(self):
        first_item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="First tattoo",
            image="artists/portfolio/first.jpg",
    )

        second_item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Second tattoo",
            image="artists/portfolio/second.jpg",
    )

        self.assertEqual(self.profile.portfolio.count(), 2)
        self.assertIn(first_item, self.profile.portfolio.all())
        self.assertIn(second_item, self.profile.portfolio.all())

    def test_portfolio_item_can_have_multiple_styles(self):
        item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Mixed style tattoo",
            image="artists/portfolio/test.jpg",
    )

        blackwork = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork",
    )

        dotwork = TattooStyle.objects.create(
            name="Dotwork",
            slug="dotwork",
    )

        item.styles.add(blackwork, dotwork)

        self.assertEqual(item.styles.count(), 2)
        self.assertIn(blackwork, item.styles.all())
        self.assertIn(dotwork, item.styles.all())

    def test_portfolio_items_are_deleted_with_artist_profile(self):
        PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Tattoo",
            image="artists/portfolio/test.jpg",
    )

        self.assertEqual(PortfolioItem.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(PortfolioItem.objects.count(), 0)

    def test_string_representation_uses_title(self):
        item = PortfolioItem.objects.create(
            artist_profile=self.profile,
            title="Blackwork sleeve",
            image="artists/portfolio/test.jpg",
    )

        self.assertEqual(str(item), "Blackwork sleeve")