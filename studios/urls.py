from django.urls import path

from .views import EmployeeServiceCreateView, MyStudioInvitationsView, StudioCreateView, StudioDetailView, StudioEmployeeListView, StudioInvitationAcceptView, StudioInvitationCreateView, StudioInvitationRejectView, StudioListView, StudioMembershipDeactivateView, StudioMembershipUpdateView, StudioUpdateView


app_name = "studios"


urlpatterns = [
    path(
        "",
        StudioListView.as_view(),
        name="studio-list",
    ),
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
    path(
        "<int:studio_pk>/employees/",
        StudioEmployeeListView.as_view(),
        name="studio-employee-list",
    ),
    path(
        "<int:studio_pk>/employees/<int:pk>/update/",
        StudioMembershipUpdateView.as_view(),
        name="studio-membership-update",
    ),
    path(
        "<int:studio_pk>/employees/<int:pk>/deactivate/",
        StudioMembershipDeactivateView.as_view(),
        name="studio-membership-deactivate",
    ),
    path(
        "<int:studio_pk>/employee-services/add/",
        EmployeeServiceCreateView.as_view(),
        name="employee-service-create",
    ),
    path(
        "invitations/",
        MyStudioInvitationsView.as_view(),
        name="my-invitations",
    ),

    path(
        "invitations/<int:pk>/accept/",
        StudioInvitationAcceptView.as_view(),
        name="invitation-accept",
    ),

    path(
        "invitations/<int:pk>/reject/",
        StudioInvitationRejectView.as_view(),
        name="invitation-reject",
    ),
]