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
                    "Categories used by existing services cannot be removed."
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
    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)

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

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)

        if professional is not None:
            self.fields["category"].queryset = professional.categories.all()
        else:
            self.fields["category"].queryset = (
                self.fields["category"].queryset.none()
            )