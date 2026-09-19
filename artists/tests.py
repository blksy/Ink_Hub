import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from .models import ArtistProfile, TattooStyle, PortfolioItem
from .forms import ArtistProfileForm
from django.urls import reverse

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

class ArtistProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.password = "ArtivaTest2026!x"

        self.artist_user = User.objects.create_user(
            email="artist-edit@example.com",
            password=self.password,
            role=User.Role.ARTIST,
        )

        self.artist = ArtistProfile.objects.create(
            user=self.artist_user,
            studio_name="Old Studio",
            location="Poznań",
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )

        self.url = reverse("artists:artist-profile-edit")

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_edit_artist_profile(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_artist_can_access_own_profile_edit_page(self):
        self.client.force_login(self.artist_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "artists/artist_profile_edit.html",
        )

    def test_artist_can_update_own_profile(self):
        self.client.force_login(self.artist_user)

        response = self.client.post(
            self.url,
            data={
                "studio_name": "New Studio",
                "bio": "Updated bio",
                "location": "Wrocław",
                "styles": [],
            },
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.studio_name,
            "New Studio",
        )
        self.assertEqual(
            self.artist.bio,
            "Updated bio",
        )
        self.assertEqual(
            self.artist.location,
            "Wrocław",
        )

        self.assertRedirects(
            response,
            reverse(
                "artists:artist-detail",
                kwargs={"pk": self.artist.pk},
            ),
        )

    def test_artist_can_only_edit_own_profile(self):
        other_user = User.objects.create_user(
            email="otherartist@example.com",
            password=self.password,
            role=User.Role.ARTIST,
        )

        other_artist = ArtistProfile.objects.create(
            user=other_user,
            studio_name="Other Studio",
            location="Warszawa",
        )

        self.client.force_login(self.artist_user)

        response = self.client.post(
            self.url,
            data={
                "studio_name": "My Updated Studio",
                "bio": "My updated bio",
                "location": "Poznań",
                "styles": [],
            },
       )

        self.artist.refresh_from_db()
        other_artist.refresh_from_db()

        self.assertEqual(
            self.artist.studio_name,
            "My Updated Studio",
        )

        self.assertEqual(
            other_artist.studio_name,
            "Other Studio",
        )

    def test_artist_can_update_styles(self):
        style1 = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-test",
        )
        style2 = TattooStyle.objects.create(
            name="Realism",
            slug="realism-test",
        )
        self.client.force_login(self.artist_user)

        response = self.client.post(
            self.url,
                data={
                "studio_name": "Test Studio",
                "bio": "Test bio",
                "location": "Poznań",
                "styles": [style1.pk, style2.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        self.artist.refresh_from_db()

        self.assertEqual(
            set(self.artist.styles.all()),
            {style1, style2},
        )
    
    def test_artist_can_update_profile_image(self):
        image = SimpleUploadedFile(
            name="profile.gif",
            content=(
                b"GIF87a\x01\x00\x01\x00\x80\x01\x00"
                b"\x00\x00\x00ccc,\x00\x00\x00\x00"
                b"\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=temp_dir):
                self.client.force_login(self.artist_user)

                response = self.client.post(
                    self.url,
                    data={
                        "studio_name": "Studio With Image",
                        "bio": "Test bio",
                       "location": "Poznań",
                        "styles": [],
                        "profile_image": image,
                    },
                )

                self.assertEqual(response.status_code, 302)

                self.artist.refresh_from_db()

                self.assertTrue(self.artist.profile_image)
                self.assertIn(
                   "artists/profile_images/",
                    self.artist.profile_image.name,
                )