
from django.conf import settings
from django.db import models

class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )

    profile_image = models.ImageField(
        upload_to="clients/profile_images/",
        blank=True,
        null=True,
    )

    phone_number = models.CharField(
        max_length=20,  
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.email