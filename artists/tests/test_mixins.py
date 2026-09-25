from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View
from django.core.exceptions import PermissionDenied
from artists.mixins import ProfessionalRequiredMixin
from django.contrib.auth.models import AnonymousUser


User = get_user_model()


class TestView(ProfessionalRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")


class ProfessionalRequiredMixinTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = TestView.as_view()

        self.professional = User.objects.create_user(
            email="professional@example.com",
            password="testpass123",
            role=User.Role.PROFESSIONAL,
        )

        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="testpass123",
            role=User.Role.CLIENT,
        )

    def test_professional_can_access_view(self):
        request = self.factory.get("/")
        request.user = self.professional
    
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

    def test_client_receives_permission_denied(self):
        request = self.factory.get("/")
        request.user = self.client_user

        with self.assertRaises(PermissionDenied):
            self.view(request)

    def test_anonymous_user_is_redirected_to_login(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = self.view(request)

        self.assertEqual(response.status_code, 302)