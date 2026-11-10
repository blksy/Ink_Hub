from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views import View
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from clients.services import create_client_profile
from django.views.generic import DetailView, UpdateView

from clients.forms import ClientProfileForm
from clients.models import ClientProfile


class ClientProfileDetailView(LoginRequiredMixin, DetailView):
    model = ClientProfile
    template_name = "clients/profile_detail.html"
    context_object_name = "client_profile"

    def get_object(self, queryset=None):
        try:
            return self.request.user.client_profile
        except ClientProfile.DoesNotExist:
            raise Http404("Profil klienta nie istnieje.")


class ClientProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ClientProfile
    form_class = ClientProfileForm
    template_name = "clients/profile_edit.html"

    def get_object(self, queryset=None):
        try:
            return self.request.user.client_profile
        except ClientProfile.DoesNotExist:
            raise Http404("Profil klienta nie istnieje.")

    def get_success_url(self):
        return reverse(
            "clients:client-profile",
        )


@method_decorator(require_POST, name="dispatch")
class ClientProfileActivateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        create_client_profile(request.user)

        return redirect("clients:client-profile")
