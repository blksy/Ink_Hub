from django.shortcuts import render
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from artists.mixins import ProfessionalRequiredMixin

from .forms import StudioForm
from .models import Studio, StudioMembership
from .mixins import StudioManagementRequiredMixin


class StudioCreateView(
    ProfessionalRequiredMixin,
    CreateView,
):
    model = Studio
    form_class = StudioForm
    template_name = "studios/studio_form.html"

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        StudioMembership.objects.create(
            studio=self.object,
            professional=self.request.user.professional_profile,
            role=StudioMembership.Role.OWNER,
            status=StudioMembership.Status.ACTIVE,
        )

        return response

    def get_success_url(self):
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": self.object.pk},
        )


class StudioDetailView(DetailView):
    model = Studio
    template_name = "studios/studio_detail.html"
    context_object_name = "studio"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        services = self.object.services.filter(
            is_active=True,
        ).select_related(
            "category",
        )

        memberships = self.object.memberships.filter(
            status=StudioMembership.Status.ACTIVE,
        ).select_related(
            "professional",
            "professional__user",
        )

        can_manage_studio = False

        if (
            self.request.user.is_authenticated
            and self.request.user.role
            == self.request.user.Role.PROFESSIONAL
        ):
            can_manage_studio = memberships.filter(
                professional=self.request.user.professional_profile,
                role__in=(
                    StudioMembership.Role.OWNER,
                    StudioMembership.Role.MANAGER,
                ),
            ).exists()

        context["services"] = services
        context["memberships"] = memberships
        context["can_manage_studio"] = can_manage_studio

        return context


class StudioUpdateView(ProfessionalRequiredMixin,  StudioManagementRequiredMixin, UpdateView):
    model = Studio
    form_class = StudioForm
    template_name = "studios/studio_form.html"

    def get_object(self, queryset=None):
        return self.studio

    def get_success_url(self):
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": self.object.pk}
        )

# class StudioDeteleView(ProfessionalRequiredMixin, StudioManagementRequiredMixin, DeleteView):

#     model=Studio

#     allowed_roles = (
        StudioMembership.Role.OWNER,
    # )

    # template_name = "studios/studio_confirm_delete.html"

    # def get_object(self, queryset=None):
    #     return self.studio

    # def get_success_url(self):