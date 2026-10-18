
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from artists.models import Category, ProfessionalProfile, TattooStyle


User = get_user_model()


class ProfessionalProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.password = "InkHubTest2026!x"

        self.professional_user = User.objects.create_user(
            email="professional-edit@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
            bio="Old bio",
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )

        self.url = reverse(
            "professionals:professional-profile-edit"
        )

    def profile_data(self, **overrides):
        data = {
            "user-first_name": "Adam",
            "user-last_name": "Kowalski",
            "bio": "Updated bio",
            "categories": [],
            "styles": [],
        }
        data.update(overrides)
        return data

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_client_cannot_edit_professional_profile(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_can_access_own_profile_edit_page(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "professionals/professional_profile_edit.html",
        )

    def test_professional_can_update_own_profile(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            data=self.profile_data(),
        )

        self.professional.refresh_from_db()
        self.professional_user.refresh_from_db()

        self.assertEqual(self.professional.bio, "Updated bio")
        self.assertEqual(self.professional_user.first_name, "Adam")
        self.assertEqual(self.professional_user.last_name, "Kowalski")

        self.assertRedirects(
            response,
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.professional.pk},
            ),
        )

    def test_professional_can_only_edit_own_profile(self):
        other_user = User.objects.create_user(
            email="otherartist@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
            first_name="Other",
        )

        other_professional = ProfessionalProfile.objects.create(
            user=other_user,
            bio="Other bio",
        )

        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            data=self.profile_data(bio="My updated bio"),
        )

        self.assertEqual(response.status_code, 302)

        self.professional.refresh_from_db()
        other_professional.refresh_from_db()
        other_user.refresh_from_db()

        self.assertEqual(self.professional.bio, "My updated bio")
        self.assertEqual(other_professional.bio, "Other bio")
        self.assertEqual(other_user.first_name, "Other")

    def test_professional_can_update_styles(self):
        tattoo_category = Category.objects.create(
             name="Tatuaż",
             slug="tatuaz",
         )

        self.professional.categories.add(tattoo_category)

        style1 = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-test",
        )
        style2 = TattooStyle.objects.create(
            name="Realism",
            slug="realism-test",
        )

        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            data=self.profile_data(
                categories=[tattoo_category.pk],
                styles=[style1.pk, style2.pk],
            ),
       )

        self.assertEqual(response.status_code, 302)

        self.professional.refresh_from_db()

        self.assertEqual(
            set(self.professional.styles.all()),
            {style1, style2},
        )

    def test_professional_can_update_categories(self):
        category = Category.objects.create(
            name="Tatuaż",
            slug="tatuaz",
        )

        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            data=self.profile_data(categories=[category.pk]),
        )

        self.assertEqual(response.status_code, 302)

        self.professional.refresh_from_db()

        self.assertIn(
            category,
            self.professional.categories.all(),
        )

    def test_professional_can_update_profile_image(self):
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
                self.client.force_login(self.professional_user)

                response = self.client.post(
                    self.url,
                    data=self.profile_data(profile_image=image),
                )

                self.assertEqual(response.status_code, 302)

                self.professional.refresh_from_db()

                self.assertTrue(self.professional.profile_image)
                self.assertIn(
                    "professionals/profile_images/",
                    self.professional.profile_image.name,
                )

    def test_invalid_form_does_not_update_profile(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(
            self.url,
            data=self.profile_data(
                bio="Changed bio",
                categories=[999999],
            ),
        )

        self.professional.refresh_from_db()
        self.professional_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.professional.bio, "Old bio")
        self.assertEqual(self.professional_user.first_name, "")
        self.assertContains(response, "Wybierz poprawną wartość")
