from django import forms

from .models import Studio


class StudioForm(forms.ModelForm):
    class Meta:
        model = Studio
        fields = (
            "name",
            "description",
            "location",
            "logo",
            "categories",
        )
        labels = {
            "name": "Nazwa studia",
            "description": "Opis",
            "location": "Lokalizacja",
            "logo": "Logo",
            "categories": "Kategorie usług",
        }