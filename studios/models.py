from django.db import models
from artists.models import ProfessionalProfile, Category
from django.core.exceptions import ValidationError


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


class EmployeeService(models.Model):
    membership = models.ForeignKey(
        StudioMembership,
        on_delete=models.CASCADE,
        related_name="employee_services",
    )

    service = models.ForeignKey(
        "artists.Service",
        on_delete=models.CASCADE,
        related_name="employee_services",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    duration_minutes = models.PositiveIntegerField()

    is_active = models.BooleanField(
        default=True,
    )


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "service"],
                name="unique_membership_service",
            )
        ]

    def __str__(self):
        return f"{self.membership.professional} - {self.service}"

    def clean(self):
        if (
            self.membership_id
            and self.service_id
            and self.membership.studio_id != self.service.studio_id
        ):
            raise ValidationError(
                {
                    "service": (
                        "Employee service must belong "
                        "to the same studio as the membership."
                    )
                }
            )