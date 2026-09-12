from django.contrib import admin

from .models import ArtistProfile, TattooStyle


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

    filter_horizontal = ("styles",)

@admin.register(TattooStyle)
class TattooStyleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }