from django.contrib import admin

from studios.models import StudioMembership

from .models import ProfessionalProfile, PortfolioItem, TattooStyle, Category, Service


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_studios",
    )

    list_select_related = ("user",)

    @admin.display(description="Studia")
    def get_studios(self, obj):
        return ", ".join(
            membership.studio.name
            for membership in obj.studio_memberships.filter(
                status=StudioMembership.Status.ACTIVE
            ).select_related("studio")
        ) or "Brak studia"


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
        "professional_profile",
        "created_at",
    )

    search_fields = (
        "title",
        "professional_profile__user__email",
        "professional_profile__studio_name",
    )

    filter_horizontal = ("styles",)

    ordering = ("-created_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
      list_display = ("name", "slug")
      search_fields = ("name",)
      prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "studio",
        "category",
        "price",
        "duration_minutes",
        "is_active",
    )

    list_filter = (
        "is_active",
        "category",
    )

    search_fields = (
        "name",
        "studio__name",
    )