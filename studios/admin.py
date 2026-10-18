from django.contrib import admin

from .models import (
    Studio,
    StudioMembership,
    StudioInvitation,
    EmployeeService,
)


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "location",
        "created_at",
    )
    search_fields = ("name", "location")
    filter_horizontal = ("categories",)


@admin.register(StudioMembership)
class StudioMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "studio",
        "professional",
        "role",
        "status",
        "joined_at",
    )
    list_filter = ("role", "status", "studio")
    search_fields = (
        "studio__name",
        "professional__user__email",
    )


@admin.register(StudioInvitation)
class StudioInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "studio",
        "email",
        "role",
        "status",
        "expires_at",
    )
    list_filter = ("role", "status")


@admin.register(EmployeeService)
class EmployeeServiceAdmin(admin.ModelAdmin):
    list_display = (
        "membership",
        "service",
        "price",
        "duration_minutes",
        "is_active",
    )
    list_filter = ("is_active",)
