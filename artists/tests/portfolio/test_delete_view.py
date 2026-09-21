from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import ProfessionalProfile, PortfolioItem


User = get_user_model()


class PortfolioItemDeleteViewTests(TestCase):
    def setUp(self):
        self.password = "InkHubTest2026!x"

        self.professional_user = User.objects.create_user(
            email="portfolio-delete@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.professional_user,
            studio_name="Delete Studio",
        )

        self.portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.professional,
            title="Tattoo to delete",
            description="This item will be deleted.",
        )

        self.client_user = User.objects.create_user(
            email="portfolio-delete-client@example.com",
            password=self.password,
            role=User.Role.CLIENT,
        )

        self.url = reverse(
            "professionals:portfolio-item-delete",
            kwargs={"pk": self.portfolio_item.pk},
        )

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_client_cannot_access_portfolio_delete_view(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_professional_can_access_own_portfolio_delete_view(self):
        self.client.force_login(self.professional_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "professionals/portfolio_item_confirm_delete.html",
        )

    def test_professional_can_delete_own_portfolio_item(self):
        self.client.force_login(self.professional_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PortfolioItem.objects.filter(
                pk=self.portfolio_item.pk
            ).exists()
        )

    def test_professional_cannot_delete_another_professionals_portfolio_item(self):
        other_user = User.objects.create_user(
            email="other-delete-artist@example.com",
            password=self.password,
            role=User.Role.PROFESSIONAL,
        )

        other_professional = ProfessionalProfile.objects.create(
            user=other_user,
            studio_name="Other Studio",
        )

        other_item = PortfolioItem.objects.create(
            professional_profile=other_professional,
            title="Other Professional Tattoo",
        )

        url = reverse(
            "professionals:portfolio-item-delete",
            kwargs={"pk": other_item.pk},
        )

        self.client.force_login(self.professional_user)

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            PortfolioItem.objects.filter(
                pk=other_item.pk
            ).exists()
        )