from django.db import models, transaction
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, ListView, View

from .forms import EmployeeServiceForm, StudioForm, StudioInvitationForm, StudioMembershipRoleForm
from .models import EmployeeService, Studio, StudioInvitation, StudioMembership
from .mixins import ActiveStudioMembershipRequiredMixin, StudioManagementRequiredMixin
from artists.mixins import ProfessionalRequiredMixin
from artists.models import PortfolioItem


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

        studio = self.object

        # 1. Aktywne usługi z katalogu studia
        services = studio.services.filter(
            is_active=True,
        ).select_related("category")

        # 2. Aktywni członkowie zespołu
        memberships = studio.memberships.filter(
            status=StudioMembership.Status.ACTIVE,
        ).select_related(
            "professional",
            "professional__user",
        )

        # 3. Aktualny użytkownik i jego uprawnienia
        current_membership = None
        can_manage_studio = False
        is_studio_member = False

        user = self.request.user

        if (
            user.is_authenticated
            and hasattr(user, "professional_profile")
        ):
            current_membership = memberships.filter(
                professional=user.professional_profile,
            ).first()

            if current_membership:
                is_studio_member = True

                can_manage_studio = current_membership.role in (
                    StudioMembership.Role.OWNER,
                    StudioMembership.Role.MANAGER,
                )

        # 4. Usługi przypisane do pracowników
        employee_services = EmployeeService.objects.filter(
            membership__studio=studio,
            membership__status=StudioMembership.Status.ACTIVE,
        ).select_related(
            "membership",
            "membership__professional",
            "membership__professional__user",
            "service",
        )

        # Goście widzą tylko aktywne usługi.
        # Właściciel i manager widzą wszystkie, także wyłączone.
        # Pracownik widzi aktywne usługi oraz własne wyłączone.
        if not can_manage_studio:
            if current_membership:
                employee_services = employee_services.filter(
                    models.Q(is_active=True)
                    | models.Q(membership=current_membership)
                )
            else:
                employee_services = employee_services.filter(
                    is_active=True,
                )
        portfolio_items = PortfolioItem.objects.filter(
            studio=studio,
        ).select_related(
            "professional_profile",
            "professional_profile__user",
            "service",
        ).prefetch_related(
            "styles",
        ).order_by("-created_at")

        context.update({
            "services": services,
            "memberships": memberships,
            "employee_services": employee_services,
            "portfolio_items": portfolio_items,
            "current_membership": current_membership,
            "is_studio_member": is_studio_member,
            "can_manage_studio": can_manage_studio,
        })

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


class EmployeeServiceCreateView(
    ActiveStudioMembershipRequiredMixin,
    CreateView,
):
    model = EmployeeService
    form_class = EmployeeServiceForm
    template_name = "studios/employee_service_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["studio"] = self.studio
        kwargs["actor_membership"] = self.studio_membership
        return kwargs

    def form_valid(self, form):
        is_manager = self.studio_membership.role in (
            StudioMembership.Role.OWNER,
            StudioMembership.Role.MANAGER,
       )

        if is_manager:
            target_membership = form.cleaned_data["membership"]
        else:
            target_membership = self.studio_membership

        service = form.cleaned_data["service"]

        already_exists = EmployeeService.objects.filter(
           membership=target_membership,
            service=service,
        ).exists()

        if already_exists:
            form.add_error(
                "service",
                "Ta usługa jest już przypisana do pracownika.",
            )
            return self.form_invalid(form)

        employee_service = form.save(commit=False)
        employee_service.membership = target_membership
        employee_service.save()

        return redirect(
            "studios:studio-detail",
            pk=self.studio.pk,
        )


class EmployeeServiceUpdateView(
    ActiveStudioMembershipRequiredMixin,
    UpdateView,
):
    model = EmployeeService
    form_class = EmployeeServiceForm
    template_name = "studios/employee_service_form.html"

    def get_queryset(self):
        queryset = EmployeeService.objects.filter(
            membership__studio=self.studio,
            membership__status=StudioMembership.Status.ACTIVE,
        ).select_related(
            "membership",
            "service",
        )

        is_manager = self.studio_membership.role in (
            StudioMembership.Role.OWNER,
            StudioMembership.Role.MANAGER,
        )

        if not is_manager:
            queryset = queryset.filter(
                membership=self.studio_membership,
            )

        return queryset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["studio"] = self.studio
        kwargs["actor_membership"] = self.studio_membership
        return kwargs

    def get_success_url(self):
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": self.studio.pk},
        )


class StudioListView(ListView):
    model = Studio
    template_name = "studios/studio_list.html"
    context_object_name = "studios"

    def get_queryset(self):
        return Studio.objects.all().order_by("name")


class MyStudioInvitationsView(
    ProfessionalRequiredMixin,
    ListView,
):
    model = StudioInvitation
    template_name = "studios/my_invitations.html"
    context_object_name = "invitations"

    def get_queryset(self):
        return (
            StudioInvitation.objects.filter(
                email__iexact=self.request.user.email,
                status=StudioInvitation.Status.PENDING,
            )
            .select_related("studio")
            .order_by("-created_at")
        )


class StudioInvitationAcceptView(
    ProfessionalRequiredMixin,
    View,
):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(
            StudioInvitation.objects.select_for_update(),
            pk=kwargs["pk"],
            email__iexact=request.user.email,
            status=StudioInvitation.Status.PENDING,
        )

        if invitation.is_expired():
            invitation.status = StudioInvitation.Status.EXPIRED
            invitation.save(update_fields=["status"])
            raise PermissionDenied("Zaproszenie wygasło.")

        if invitation.role == StudioMembership.Role.OWNER:
            raise PermissionDenied(
                "Nie można przyjąć zaproszenia jako właściciel."
            )

        professional = request.user.professional_profile

        membership, created = (
            StudioMembership.objects.select_for_update().get_or_create(
                studio=invitation.studio,
                professional=professional,
                defaults={
                    "role": invitation.role,
                    "status": StudioMembership.Status.ACTIVE,
                },
            )
        )

        if not created:
            if membership.status == StudioMembership.Status.ACTIVE:
                raise PermissionDenied(
                    "Jesteś już aktywnym członkiem tego studia."
                )

            membership.role = invitation.role
            membership.status = StudioMembership.Status.ACTIVE
            membership.save(update_fields=["role", "status"])

        invitation.status = StudioInvitation.Status.ACCEPTED
        invitation.save(update_fields=["status"])

        return redirect(
            "studios:studio-detail",
            pk=invitation.studio.pk,
        )


class StudioInvitationRejectView(
    ProfessionalRequiredMixin,
    View,
):
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(
            StudioInvitation,
            pk=kwargs["pk"],
            email__iexact=request.user.email,
            status=StudioInvitation.Status.PENDING,
        )

        if invitation.is_expired():
            invitation.status = StudioInvitation.Status.EXPIRED
        else:
            invitation.status = StudioInvitation.Status.REJECTED

        invitation.save(update_fields=["status"])

        return redirect("studios:my-invitations")