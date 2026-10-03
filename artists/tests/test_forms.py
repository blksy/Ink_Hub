from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from decimal import Decimal
from artists.forms import ProfessionalProfileForm, PortfolioItemForm
from artists.models import (
    ProfessionalProfile,
    TattooStyle, 
    Service, 
    Category,
)
from studios.models import (
    EmployeeService,
    Studio,
    StudioMembership,
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

        self.studio = Studio.objects.create(
            name="Ink House",
            location="Poznań",
        )

        self.studio.categories.add(self.category)

        self.membership = StudioMembership.objects.create(
            studio=self.studio,
            professional=self.professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        self.service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Tattoo session",
            price=Decimal("500.00"),
        )

        self.employee_service = EmployeeService.objects.create(
            membership=self.membership,
            service=self.service,
            price=Decimal("500.00"),
            duration_minutes=120,
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

    def test_service_field_contains_only_services_assigned_to_professional(self):
        other_user = User.objects.create_user(
            email="other-professional@example.com",
            password="InkHubTest2026!x",
            role=User.Role.PROFESSIONAL,
        )

        other_professional = ProfessionalProfile.objects.create(
            user=other_user,
        )

        other_studio = Studio.objects.create(
            name="Other Studio",
            location="Poznań",
        )

        other_studio.categories.add(self.category)

        other_membership = StudioMembership.objects.create(
            studio=other_studio,
            professional=other_professional,
            role=StudioMembership.Role.EMPLOYEE,
        )

        other_service = Service.objects.create(
            studio=other_studio,
            category=self.category,
            name="Other service",
            price=Decimal("300.00"),
        )

        EmployeeService.objects.create(
            membership=other_membership,
            service=other_service,
            price=Decimal("300.00"),
            duration_minutes=60,
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
    
    def test_service_field_excludes_unassigned_service_from_same_studio(self):
        unassigned_service = Service.objects.create(
            studio=self.studio,
            category=self.category,
            name="Piercing consultation",
            price=Decimal("200.00"),
        )

        form = PortfolioItemForm(
            professional=self.professional,
        )

        queryset = form.fields["service"].queryset

        self.assertIn(self.service, queryset)
        self.assertNotIn(unassigned_service, queryset)