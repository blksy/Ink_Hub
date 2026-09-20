import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from artists.models import ArtistProfile, TattooStyle


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


class ArtistProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.password =  "InkHubTest2026!x"

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

    def test_invalid_form_does_not_update_profile(self):
        self.client.force_login(self.artist_user)

        response = self.client.post(
            self.url,
            data={
                "studio_name": "Changed Studio",
                "bio": "Changed bio",
                "location": "Warszawa",
                "styles": [999999],
            },
        )

        self.artist.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.artist.studio_name,
            "Old Studio",
        )
        self.assertEqual(
            self.artist.location,
            "Poznań",
        )