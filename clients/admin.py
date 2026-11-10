from django.contrib import admin

from clients.models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "phone_number",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__email",
        "phone_number",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = ("user",)

    @admin.display(description="Email użytkownika")
    def user_email(self, obj):
        return obj.user.email
