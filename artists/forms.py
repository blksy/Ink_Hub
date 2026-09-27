from django import forms

from .models import ProfessionalProfile, PortfolioItem, Service


class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        fields = (
            "studio_name",
            "bio",
            "location",
            "profile_image",
            "categories",
            "styles",
        )

        labels = {
            "studio_name": "Nazwa studia / salonu",
            "bio": "Opis",
            "location": "Lokalizacja",
            "profile_image": "Zdjęcie profilowe / logo",
            "categories": "Kategorie usług",
            "styles": "Style tatuażu",
        }

        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "styles": forms.CheckboxSelectMultiple(),
        }

    def clean_categories(self):
        categories = self.cleaned_data["categories"]

        if self.instance.pk:
            used_category_ids = set(
                self.instance.services.values_list(
                   "category_id",
                    flat=True,
                )
            )

            selected_category_ids = set(
                categories.values_list(
                    "id",
                    flat=True,
                )
            )
    
            if not used_category_ids.issubset(selected_category_ids):
                raise forms.ValidationError(
                     "Nie można usunąć kategorii używanej przez istniejące usługi."
                )

        return categories


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = (
            "title",
            "description",
            "image",
            "service",
            "styles",
            "final_price",
            "sessions_count",
        )

        labels = {
            "title": "Tytuł",
            "description": "Opis",
            "image": "Zdjęcie",
            "service": "Usługa",
            "styles": "Style tatuażu",
            "final_price": "Cena realizacji",
            "sessions_count": "Liczba sesji (opcjonalnie)",
        }

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["service"].empty_label = "Brak powiązanej usługi"

        if professional is not None:
            self.fields["service"].queryset = professional.services.all()
        else:
            self.fields["service"].queryset = (
                self.fields["service"].queryset.none()
            )

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

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "Wybierz kategorię"

        if professional is not None:
            self.fields["category"].queryset = professional.categories.all()
        else:
            self.fields["category"].queryset = (
                self.fields["category"].queryset.none()
            )