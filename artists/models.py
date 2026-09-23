from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class TattooStyle(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProfessionalProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_profile",
    )
    studio_name = models.CharField(
        max_length=150,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="professionals/profile_images/",
        blank=True,
        null=True,
    )

    categories = models.ManyToManyField(
        Category,
        related_name="professionals",
        blank=True,
    )

    styles = models.ManyToManyField(
        TattooStyle,
        related_name="professionals",
        blank=True,
    )

    def clean(self):
        if self.user.role != self.user.Role.PROFESSIONAL:
            raise ValidationError(
                "Professional profile can only be created for users with PROFESSIONAL role."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.studio_name or self.user.email


class PortfolioItem(models.Model):
    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="portfolio",
    )

    image = models.ImageField(
        upload_to="professionals/portfolio/",
    )

    description = models.TextField(
        blank=True,
    )

    title = models.CharField(
        max_length=150,
        blank=True,
    )

    styles = models.ManyToManyField(
        TattooStyle,
        related_name="portfolio_items",
        blank=True,
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )    

    sessions_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title or f"Portfolio item #{self.pk}"


class Service(models.Model):
    professional = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="services",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="services",
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.professional_id
            and self.category_id
            and not self.professional.categories.filter(
                pk=self.category_id
            ).exists()
        ):
            raise ValidationError(
                {
                    "category": (
                        "Service category must be assigned "
                        "to the professional profile."
                    )
                }
            )

    def __str__(self):
        return self.name