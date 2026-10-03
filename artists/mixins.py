from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from studios.models import Studio, StudioMembership


class ProfessionalRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.role != request.user.Role.PROFESSIONAL
        ):
            raise PermissionDenied(
                "Only professionals can access this page."
            )

        return super().dispatch(request, *args, **kwargs)


class StudioManagementRequiredMixin:
    allowed_roles = (
        StudioMembership.Role.OWNER,
        StudioMembership.Role.MANAGER,
    )

    def dispatch(self, request, *args, **kwargs):
        self.studio = get_object_or_404(
            Studio,
            pk=kwargs["studio_pk"],
        )

        membership = StudioMembership.objects.filter(
            studio=self.studio,
            professional=request.user.professional_profile,
            status=StudioMembership.Status.ACTIVE,
        ).first()

        if (
            membership is None
            or membership.role not in self.allowed_roles
        ):
            raise PermissionDenied

        self.studio_membership = membership

        return super().dispatch(request, *args, **kwargs)