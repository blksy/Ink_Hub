from django.shortcuts import render
from django.db import transaction
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, ListView, View

from .forms import StudioForm, StudioInvitationForm, StudioMembershipRoleForm
from .models import Studio, StudioInvitation, StudioMembership
from .mixins import StudioManagementRequiredMixin
from artists.mixins import ProfessionalRequiredMixin


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


class StudioInvitationCreateView (StudioManagementRequiredMixin,CreateView):
    model = StudioInvitation
    form_class = StudioInvitationForm
    template_name = "studios/studio_invitation_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["studio"] = self.studio
        return kwargs 

    def form_valid(self, form):
        form.instance.studio = self.studio
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": self.studio.pk},
        )


class StudioEmployeeListView(StudioManagementRequiredMixin,ListView,):
    model = StudioMembership
    template_name = "studios/studio_employee_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return self.studio.memberships.filter(
            studio=self.studio,
            status=StudioMembership.Status.ACTIVE,
        ).select_related(
            "professional",
            "professional__user",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_studio"] = True
        context["studio"] = self.studio
        context["is_owner"] = (
            self.studio_membership.role == StudioMembership.Role.OWNER
        )
        return context


class StudioMembershipUpdateView(StudioManagementRequiredMixin, UpdateView):
    allowed_roles = (
        StudioMembership.Role.OWNER,
    )
    model = StudioMembership
    form_class = StudioMembershipRoleForm
    template_name = "studios/studio_membership_form.html"

    def get_queryset(self): 
        return self.studio.memberships.filter(
            status=StudioMembership.Status.ACTIVE,
        ).exclude(
            role=StudioMembership.Role.OWNER,
        )

    def get_success_url(self):
        return reverse(
            "studios:studio-employee-list",
            kwargs={"studio_pk": self.studio.pk},
        )


  
class StudioMembershipDeactivateView(
    StudioManagementRequiredMixin,
    View,
):
    def post(self, request, *args, **kwargs):
        membership = get_object_or_404(
            StudioMembership,
            pk=kwargs["pk"],
            studio=self.studio,
            status=StudioMembership.Status.ACTIVE,
        )

        if membership.role == StudioMembership.Role.OWNER:
            raise PermissionDenied

        if (
            self.studio_membership.role == StudioMembership.Role.MANAGER
            and membership.role == StudioMembership.Role.MANAGER
        ):
            raise PermissionDenied

        membership.status = StudioMembership.Status.INACTIVE
        membership.save(update_fields=["status"])

        return redirect(
            "studios:studio-employee-list",
            studio_pk=self.studio.pk,
        )