from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from artists.models import PortfolioItem, ProfessionalProfile, TattooStyle


User = get_user_model()


class PortfolioItemModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolioartist@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.profile = ProfessionalProfile.objects.create(
            user=self.user,
            studio_name="Ink House",
        )

    def test_create_portfolio_item(self):
        item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork sleeve",
            description="Full sleeve tattoo.",
            image="professionals/portfolio/test.jpg",
    )

        self.assertEqual(item.professional_profile, self.profile)
        self.assertEqual(item.title, "Blackwork sleeve")
        self.assertEqual(item.description, "Full sleeve tattoo.")

    def test_professional_profile_can_have_multiple_portfolio_items(self):
        first_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="First tattoo",
            image="professionals/portfolio/first.jpg",
    )

        second_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Second tattoo",
            image="professionals/portfolio/second.jpg",
    )

        self.assertEqual(self.profile.portfolio.count(), 2)
        self.assertIn(first_item, self.profile.portfolio.all())
        self.assertIn(second_item, self.profile.portfolio.all())

    def test_portfolio_item_can_have_multiple_styles(self):
        item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Mixed style tattoo",
            image="professionals/portfolio/test.jpg",
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

    def test_portfolio_items_are_deleted_with_professional_profile(self):
        PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Tattoo",
            image="professionals/portfolio/test.jpg",
    )

        self.assertEqual(PortfolioItem.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(PortfolioItem.objects.count(), 0)

    def test_string_representation_uses_title(self):
        item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork sleeve",
            image="professionals/portfolio/test.jpg",
    )

        self.assertEqual(str(item), "Blackwork sleeve")

    def test_portfolio_item_can_store_price_and_sessions(self):
        portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Blackwork sleeve",
            image="test.jpg",
            final_price=Decimal("2400.00"),
            sessions_count=3,
    )

        self.assertEqual(portfolio_item.final_price, Decimal("2400.00"))
        self.assertEqual(portfolio_item.sessions_count, 3)

    def test_portfolio_price_and_sessions_are_optional(self):
        portfolio_item = PortfolioItem.objects.create(
            professional_profile=self.profile,
            title="Small tattoo",
            image="test.jpg",
    )

        self.assertIsNone(portfolio_item.final_price)
        self.assertIsNone(portfolio_item.sessions_count)
