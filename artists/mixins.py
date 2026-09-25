from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


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