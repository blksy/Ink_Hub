from django import forms

from .models import ProfessionalProfile, PortfolioItem


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
        )