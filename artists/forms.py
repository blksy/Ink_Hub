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


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = (
            "title",
            "description",
            "image",
            "styles",
            "final_price",
            "sessions_count",
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