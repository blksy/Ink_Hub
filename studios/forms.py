from django import forms
from django.core.exceptions import ValidationError
from .models import EmployeeService, Studio, StudioInvitation, StudioMembership


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

    def clean_role(self):
        role = self.cleaned_data["role"]
    
        if role == StudioMembership.Role.OWNER:
            raise ValidationError(
                "Nie można zaprosić użytkownika jako właściciela studia."
            )
    
        return role


class StudioMembershipRoleForm(forms.ModelForm):
    class Meta:
        model = StudioMembership
        fields = ("role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["role"].choices = [
            (role, label)
            for role, label in StudioMembership.Role.choices
            if role != StudioMembership.Role.OWNER
        ]


class EmployeeServiceForm(forms.ModelForm):
    membership =  forms.ModelChoiceField(
        queryset=StudioMembership.objects.none(),
        required=False,
        label="Pracownik",
    )


    class Meta:
        model = EmployeeService
        fields = (
            "service",
            "price",
            "duration_minutes",
        )

    def __init__(self, *args, **kwargs):
        studio = kwargs.pop("studio")
        actor_membership = kwargs.pop("actor_membership")

        super().__init__(*args, **kwargs)

        self.fields["service"].queryset = studio.services.filter(
            is_active=True,
        )

        is_manager = actor_membership.role in (
            StudioMembership.Role.OWNER,
            StudioMembership.Role.MANAGER,
        )

        if is_manager:
            self.fields["membership"].queryset = (
                studio.memberships.filter(
                    status=StudioMembership.Status.ACTIVE,
                )
            )
            self.fields["membership"].required = True
        else:
            del self.fields["membership"]