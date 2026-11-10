
from django.contrib import admin
from django.test import TestCase

from clients.admin import ClientProfileAdmin
from clients.models import ClientProfile


class ClientProfileAdminTests(TestCase):

    def test_client_profile_is_registered(self):
        self.assertIn(ClientProfile, admin.site._registry)

    def test_admin_searches_by_user_email(self):
        model_admin = admin.site._registry[ClientProfile]

        self.assertIn(
            "user__email",
            model_admin.search_fields,
        )

    def test_admin_displays_phone_number(self):
        model_admin = admin.site._registry[ClientProfile]

        self.assertIn(
            "phone_number",
            model_admin.list_display,
        )

    def test_admin_displays_user_email(self):
        model_admin = admin.site._registry[ClientProfile]

        self.assertIn(
            "user_email",
            model_admin.list_display,
        )
