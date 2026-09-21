from artists.models import ProfessionalProfile
from django.db import transaction
from .models import User


class UserFactory:
    @staticmethod
    @transaction.atomic
    def create_user(email, password, role):
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
        )

        if role == User.Role.PROFESSIONAL:
            ProfessionalProfile.objects.create(user=user)

        return user