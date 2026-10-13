from django.urls import path

from .views import StudioCreateView, StudioDetailView, StudioInvitationCreateView, StudioUpdateView


app_name = "studios"


urlpatterns = [
    path(
        "create/",
        StudioCreateView.as_view(),
        name="studio-create",
    ),
    path(
        "<int:pk>/",
        StudioDetailView.as_view(),
        name="studio-detail",
    ),
    path(
        "<int:studio_pk>/edit/",
        StudioUpdateView.as_view(),
        name="studio-update",
    ),
    path(
        "<int:studio_pk>/invitations/create/",
        StudioInvitationCreateView.as_view(),
        name="studio-invitation-create",
    ),
]