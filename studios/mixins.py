
from studios.models import StudioMembership, Studio
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


class ActiveStudioMembershipRequiredMixin:
    def check_studio_permission(self):
        return True
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        
        if not hasattr(request.user, "professional_profile"):
            raise PermissionDenied

        self.studio = get_object_or_404(
            Studio,
            pk=kwargs["studio_pk"],
        )
        membership = StudioMembership.objects.filter(
            studio=self.studio,
            professional=request.user.professional_profile,
            status=StudioMembership.Status.ACTIVE,
        ).first()

        if membership is None:
            raise PermissionDenied

        self.studio_membership = membership

        if not self.check_studio_permission():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs) 


class StudioManagementRequiredMixin(ActiveStudioMembershipRequiredMixin):
    allowed_roles = (
        StudioMembership.Role.OWNER,
        StudioMembership.Role.MANAGER,
    )

    def check_studio_permission(self):
        return self.studio_membership.role in self.allowed_roles
