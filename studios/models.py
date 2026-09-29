from django.db import models
from artists.models import ProfessionalProfile, Category


class Studio(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
    logo = models.ImageField(
        upload_to="studios/logos/",
        blank=True,
        null=True,
    )
    categories = models.ManyToManyField(
        Category,
        related_name="studios",
        blank=True,
    )
    members = models.ManyToManyField(
        ProfessionalProfile,
        through="StudioMembership",
        related_name="studios",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StudioMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    studio = models.ForeignKey(
        Studio,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="studio_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["studio", "professional"],
                name="unique_studio_professional_membership",
            )
        ]

    def __str__(self):
        return (
            f"{self.professional} - "
            f"{self.studio} ({self.get_role_display()})"
        )