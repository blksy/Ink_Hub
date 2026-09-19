from django import forms

from .models import ArtistProfile


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