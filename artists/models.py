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

class ArtistProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artist_profile",
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
        upload_to="artists/profile_images/",
        blank=True,
        null=True,
    )

    styles = models.ManyToManyField(
        TattooStyle,
        related_name="artists",
        blank=True,
    )

    def clean(self):
        if self.user.role != self.user.Role.ARTIST:
            raise ValidationError(
                "Artist profile can only be created for users with ARTIST role."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.studio_name or self.user.email

class PortfolioItem(models.Model):
    artist_profile = models.ForeignKey(
        ArtistProfile,
        on_delete=models.CASCADE,
        related_name="portfolio",
    )

    image = models.ImageField(
        upload_to="artists/portfolio/",
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title or f"Portfolio item #{self.pk}"