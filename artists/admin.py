from django.contrib import admin

from .models import ArtistProfile, PortfolioItem, TattooStyle


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

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artist_profile",
        "created_at",
    )

    search_fields = (
        "title",
        "artist_profile__user__email",
        "artist_profile__studio_name",
    )

    filter_horizontal = ("styles",)

    ordering = ("-created_at",)