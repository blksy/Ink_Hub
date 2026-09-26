from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from decimal import Decimal
from artists.forms import ProfessionalProfileForm, PortfolioItemForm, ServiceForm
from artists.models import (
    ProfessionalProfile,
    TattooStyle, 
    Service, 
    Category,
)

User = get_user_model()

class ProfessionalProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="formartist@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-form-test",
        )

    def test_form_is_valid_with_correct_data(self):
        form = ProfessionalProfileForm(
            data={
                "studio_name": "Black Moon Tattoo",
                "bio": "Tattoo artist from Poznań.",
                "location": "Poznań",
                "styles": [self.style.pk],
            },
            instance=self.professional,
        )

        self.assertTrue(form.is_valid())

    def test_form_does_not_expose_user_field(self):
        form = ProfessionalProfileForm(
            instance=self.professional
        )

        self.assertNotIn("user", form.fields)

    def test_form_contains_expected_fields(self):
        form = ProfessionalProfileForm(
            instance=self.professional
        )

        self.assertEqual(
            set(form.fields.keys()),
            {
                "studio_name",
                "bio",
                "location",
                "profile_image",
                "categories",
                "styles",
            },
        )

    def test_professional_profile_form_can_assign_categories(self):
        category_one = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        category_two = Category.objects.create(
            name="Piercing",
            slug="piercing",
        )
    
        form = ProfessionalProfileForm(
            data={
                "studio_name": "Dark Ink Studio",
                "bio": "Tattoo and piercing studio.",
                 "location": "Poznań",
                "categories": [
                    category_one.pk,
                    category_two.pk,
                ],
                   "styles": [],
            },
            instance=self.professional,
         )
    
        self.assertTrue(form.is_valid())
    
        professional = form.save()
    
        self.assertEqual(professional.categories.count(), 2)
        self.assertIn(
            category_one,
            professional.categories.all(),
        )
        self.assertIn(
            category_two,
            professional.categories.all(),
        )

    def test_cannot_remove_category_used_by_existing_service(self):
        category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        self.professional.categories.add(category)

        Service.objects.create(
            professional=self.professional,
            category=category,
           name="Haircut",
            price=Decimal("100.00"),
        )

        form = ProfessionalProfileForm(
            data={
                "studio_name": "Beauty Studio",
                "bio": "Beauty services.",
                "location": "Poznań",
                "categories": [],
                "styles": [],
            },
            instance=self.professional,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("categories", form.errors)

    def test_can_remove_category_not_used_by_service(self):
        used_category = Category.objects.create(
            name="Hair",
            slug="hair",
        )

        unused_category = Category.objects.create(
            name="Nails",
            slug="nails",
        )

        self.professional.categories.add(
            used_category,
            unused_category,
        )

        Service.objects.create(
            professional=self.professional,
            category=used_category,
            name="Haircut",
            price=Decimal("100.00"),
        )

        form = ProfessionalProfileForm(
            data={
                "studio_name": "Beauty Studio",
                "bio": "Beauty services.",
                "location": "Poznań",
                "categories": [used_category.pk],
                "styles": [],
            },
            instance=self.professional,
        )

        self.assertTrue(form.is_valid(), form.errors)

        professional = form.save()

        self.assertIn(
            used_category,
            professional.categories.all(),
        )
        self.assertNotIn(
            unused_category,
            professional.categories.all(),
        )


class PortfolioItemFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="portfolio-form@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        self.professional = ProfessionalProfile.objects.create(
            user=self.user,
        )

        self.style = TattooStyle.objects.create(
            name="Blackwork",
            slug="blackwork-form-test",
        )

        self.category = Category.objects.create(
            name="Tattoo",
            slug="tattoo",
        )

        self.professional.categories.add(self.category)

        self.service = Service.objects.create(
            professional=self.professional,
            category=self.category,
            name="Tattoo session",
            price=Decimal("500.00"),
        )

    def create_test_image(self):
        image_file = BytesIO()

        image = Image.new("RGB", (100, 100))
        image.save(image_file, "JPEG")

        image_file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg",
    )

    def test_form_contains_expected_fields(self):
        form = PortfolioItemForm()

        self.assertEqual(
            set(form.fields.keys()),
            {
                "title",
                "description",
                "image",
                "service",
                "styles",
                "final_price",
                "sessions_count", 
            },
        )

    def test_form_does_not_expose_professional_profile(self):
        form = PortfolioItemForm()

        self.assertNotIn(
            "professional_profile",
            form.fields,
        )

    def test_portfolio_form_contains_price_and_sessions_fields(self):
        form = PortfolioItemForm()

        self.assertIn("final_price", form.fields)
        self.assertIn("sessions_count", form.fields)

    def test_portfolio_form_accepts_price_and_sessions(self):
        image = self.create_test_image()

        form = PortfolioItemForm(
            data={
                "title": "Blackwork sleeve",
                "description": "Full sleeve project",
                "final_price": "2400.00",
                "sessions_count": 3,
            },
            files={
                "image": image,
            },
            professional=self.professional,
        )
    
        self.assertTrue(form.is_valid(), form.errors)

    def test_portfolio_form_allows_empty_price_and_sessions(self):
        form = PortfolioItemForm()

        self.assertFalse(form.fields["final_price"].required)
        self.assertFalse(form.fields["sessions_count"].required)

    def test_service_field_contains_only_professionals_services(self):
        other_user = User.objects.create_user(
            email="other-professional@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        other_professional = ProfessionalProfile.objects.create(
            user=other_user,
        )

        other_professional.categories.add(self.category)

        other_service = Service.objects.create(
            professional=other_professional,
            category=self.category,
            name="Other service",
            price=Decimal("300.00"),
        )

        form = PortfolioItemForm(
            professional=self.professional
        )

        queryset = form.fields["service"].queryset

        self.assertIn(self.service, queryset)
        self.assertNotIn(other_service, queryset)

    def test_service_field_is_empty_without_professional(self):
        form = PortfolioItemForm()

        self.assertFalse(
            form.fields["service"].queryset.exists()
        )
    
