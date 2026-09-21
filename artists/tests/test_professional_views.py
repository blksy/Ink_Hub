from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from artists.models import ProfessionalProfile, PortfolioItem, Category, TattooStyle


User = get_user_model()


class ProfessionalViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="viewartist@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Black Clover Tattoo",
            location="Poznań",
            bio="Tattoo artist from Poznań.",
        )

    def test_professional_list_view_returns_200(self):
        response = self.client.get(
            reverse("professionals:professional-list")
        )

        self.assertEqual(response.status_code, 200)

    def test_professional_list_view_uses_correct_template(self):
        response = self.client.get(
            reverse("professionals:professional-list")
        )

        self.assertTemplateUsed(
            response,
            "professionals/professional_list.html",
        )

    def test_professional_list_contains_professional(self):
        response = self.client.get(
            reverse("professionals:professional-list")
        )

        self.assertContains(
            response,
            "Black Clover Tattoo",
        )

    def test_professional_detail_view_returns_200(self):
        response = self.client.get(
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
    
    def test_professional_detail_displays_portfolio_item(self):
        portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork Sleeve",
            description="Full sleeve tattoo.",
            image="professionals/portfolio/test.jpg",
        )

        response = self.client.get(
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, portfolio_item.title)
        self.assertContains(response, portfolio_item.description)

    def test_professional_sees_portfolio_management_links_on_own_profile(self):
        portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork Sleeve",
            image="professionals/portfolio/test.jpg",
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertContains(response, "Dodaj pracę")
        self.assertContains(response, "Edytuj")
        self.assertContains(response, "Usuń")

        self.assertContains(
            response,
            reverse(
                "professionals:portfolio-item-update",
                kwargs={"pk": portfolio_item.pk},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "professionals:portfolio-item-delete",
                kwargs={"pk": portfolio_item.pk},
            ),
        )

    def test_other_professional_does_not_see_portfolio_management_links(self):
        portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork Sleeve",
            image="professionals/portfolio/test.jpg",
        )

        other_user = User.objects.create_user(
            email="other-viewer@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        ProfessionalProfile.objects.create(
            user=other_user,
            studio_name="Other Studio",
        )

        self.client.force_login(other_user)

        response = self.client.get(
            reverse(
                "professionals:professional-detail",
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
                "professionals:portfolio-item-update",
                kwargs={"pk": portfolio_item.pk},
            ),
        )
        self.assertNotContains(
            response,
            reverse(
                "professionals:portfolio-item-delete",
                kwargs={"pk": portfolio_item.pk},
            ),
        )

    def test_professional_detail_displays_categories(self):
        tattoo = Category.objects.create(
            name="Tatuaż",
            slug="tatuaz",
        )
        piercing = Category.objects.create(
            name="Piercing",
            slug="piercing",
        )

        self.profile.categories.add(tattoo, piercing)

        response = self.client.get(
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tatuaż")
        self.assertContains(response, "Piercing")

    def test_professional_detail_without_tattoo_styles_does_not_display_styles_section(self):
        response = self.client.get(
            reverse(
                "professionals:professional-detail",
                kwargs={"pk": self.profile.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Style tatuażu")