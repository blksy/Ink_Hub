from django.db import models


class Studio(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
    logo = models.ImageField(
        upload_to="studios/logos/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name