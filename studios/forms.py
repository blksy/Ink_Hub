from django import forms
from django.core.exceptions import ValidationError
from .models import Studio, StudioInvitation, StudioMembership


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

class StudioInvitationForm(forms.ModelForm):
    class Meta:
        model = StudioInvitation
        fields =(
            "email",
            "role"
        )


    def __init__(self, *args, studio=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.studio = studio

    def clean_email(self):
        email = self.cleaned_data["email"]

        membership_exists = StudioMembership.objects.filter(
        studio=self.studio,
        professional__user__email__iexact=email,
        status=StudioMembership.Status.ACTIVE,
    ).exists()

        if membership_exists:
            raise ValidationError(
                "Ten użytkownik jest już pracownikiem tego studia."
            )
        
        invitation_exist = StudioInvitation.objects.filter(
        studio=self.studio,
        email__iexact=email,
        status=StudioInvitation.Status.PENDING,
     ).exists()

        if invitation_exist:
           raise ValidationError(
               "Oczekujące zaproszenie na ten adres e-mail już istnieje."
           )
        return email


    