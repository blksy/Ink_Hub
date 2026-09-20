from django import forms

from .models import ArtistProfile, PortfolioItem


class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = (
            "studio_name",
            "bio",
            "location",
            "profile_image",
            "styles",
        )


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = (
            "title",
            "description",
            "image",
            "styles",
        )