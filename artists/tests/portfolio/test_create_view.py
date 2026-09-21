import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from artists.models import ProfessionalProfile, PortfolioItem, TattooStyle


User = get_user_model()


class PortfolioItemCreateViewTests(TestCase):
    def setUp(self):
        self.password = "ArtivaTest2026!x"

        self.professional_user = User.objects.create_user(
            email="portfolio-artist@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
            studio_name="Portfolio Studio",
        )

        self.client_user = User.objects.create_user(
            email="portfolio-client@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )    

        self.url = reverse("professionals:portfolio-item-create")

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_access_portfolio_create_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_can_access_portfolio_create_view(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "professionals/portfolio_item_form.html",
        )

    def test_professional_can_create_portfolio_item(self):
        image = SimpleUploadedFile(
            name="portfolio.gif",
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
                    data={
                        "title": "Blackwork Tattoo",
                        "description": "Blackwork sleeve project.",
                        "image": image,
                        "styles": [],
                    },
                )

                self.assertEqual(response.status_code, 302)
                self.assertEqual(PortfolioItem.objects.count(), 1)

                portfolio_item = PortfolioItem.objects.get()

                self.assertEqual(
                    portfolio_item.title,
                    "Blackwork Tattoo",
                )
                self.assertEqual(
                    portfolio_item.professional_profile,
                    self.professional,
                )

    def test_professional_can_create_portfolio_item_with_styles(self):
        style = TattooStyle.objects.create(
            name="Neo Traditional",
            slug="neo-traditional-portfolio",
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

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=temp_dir):
                self.client.force_login(self.professional_user)

                response = self.client.post(
                    self.url,
                    data={
                        "title": "Neo Traditional Tattoo",
                        "description": "Portfolio test.",
                        "image": image,
                        "styles": [style.pk],
                    },
                )

                self.assertEqual(response.status_code, 302)

                portfolio_item = PortfolioItem.objects.get()

                self.assertIn(
                    style,
                    portfolio_item.styles.all(),
                )