from django import forms
from django.contrib.auth import get_user_model
from .models import Category, ProfessionalProfile, PortfolioItem, Service
from studios.models import Studio, StudioMembership

User = get_user_model()


class UserPersonalDataForm(forms.ModelForm):
    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
        )

        labels = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
        }


class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile

        fields = (
            "bio",
            "profile_image",
            "categories",
            "styles",
        )

        labels = {
            "bio": "O mnie",
            "profile_image": "Zdjęcie profilowe",
            "categories": "Specjalizacje",
            "styles": "Style tatuażu",
        }

        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "styles": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        is_tattoo_artist = False

        if self.is_bound:
            if hasattr(self.data, "getlist"):
                selected_categories = self.data.getlist("categories")
            else:
                selected_categories = self.data.get("categories", [])

                if not isinstance(selected_categories, (list, tuple)):
                    selected_categories = [selected_categories]

            is_tattoo_artist = Category.objects.filter(
                pk__in=selected_categories,
                slug="tatuaz",
            ).exists()

        elif self.instance.pk:
            is_tattoo_artist = self.instance.categories.filter(
                slug="tatuaz",
            ).exists()

        if not is_tattoo_artist:
            self.fields.pop("styles", None)


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem

        fields = (
            "title",
            "description",
            "image",
            "studio",
            "service",
            "styles",
            "final_price",
            "sessions_count",
        )

        labels = {
            "title": "Tytuł",
            "description": "Opis",
            "image": "Zdjęcie",
            "studio": "Studio, w którym wykonano pracę",
            "service": "Usługa",
            "styles": "Style tatuażu",
            "final_price": "Cena realizacji",
            "sessions_count": "Liczba sesji (opcjonalnie)",
        }

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.professional = professional

        self.fields["studio"].required = False
        
        self.fields["studio"].empty_label = "Bez przypisanego studia"

        self.fields["service"].empty_label = "Brak powiązanej usługi"

        if professional is not None:
            active_memberships = StudioMembership.objects.filter(
                professional=professional,
                status=StudioMembership.Status.ACTIVE,
            )

            self.fields["studio"].queryset = Studio.objects.filter(
                memberships__in=active_memberships,
            ).distinct()

            self.fields["service"].queryset = Service.objects.filter(
                employee_services__membership__in=active_memberships,
                employee_services__is_active=True,
                is_active=True,
            ).distinct()

        else:
            self.fields["studio"].queryset = Studio.objects.none()
            self.fields["service"].queryset = Service.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        studio = cleaned_data.get("studio")
        service = cleaned_data.get("service")

        if studio and service and service.studio_id != studio.pk:
            self.add_error(
                "service",
                "Wybrana usługa nie należy do wskazanego studia.",
            )

        return cleaned_data


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = (
            "category",
            "name",
            "description",
            "price",
            "duration_minutes",
            "is_active",
        )

        labels = {
            "category": "Kategoria",
            "name": "Nazwa usługi",
            "description": "Opis",
            "price": "Cena",
            "duration_minutes": "Czas trwania (minuty)",
            "is_active": "Usługa aktywna",
        }

    def __init__(self, *args, studio=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "Wybierz kategorię"

        if studio is not None:
            self.instance.studio = studio
            self.fields["category"].queryset = studio.categories.all()
        else:
            self.fields["category"].queryset = (
                self.fields["category"].queryset.none()
            )