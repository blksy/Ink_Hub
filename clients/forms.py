from django import forms
from django.db import transaction

from clients.models import ClientProfile


class ClientProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Imię",
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nazwisko",
    )

    class Meta:
        model = ClientProfile

        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
        )

        labels = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
            "phone_number": "Numer telefonu",
            "profile_image": "Zdjęcie profilowe"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            instance_user = self.instance.user
   
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name


    def save(self, commit=True):
        client_profile = super().save(commit=False)

        user = client_profile.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            with transaction.atomic():
                user.save(update_fields=["first_name", "last_name"])
                client_profile.save()
                self.save_m2m()

        return client_profile