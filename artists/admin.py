from django.contrib import admin

from .models import ArtistProfile


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "studio_name",
        "location",
    )

    search_fields = (
        "user__email",
        "studio_name",
        "location",
    )
