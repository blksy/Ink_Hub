from artists.models import ProfessionalProfile
from django.db import transaction

from clients.models import ClientProfile
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
        elif role == User.Role.CLIENT:
            ClientProfile.objects.create(user=user)

        return user