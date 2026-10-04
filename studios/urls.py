from django.urls import path

from .views import StudioCreateView, StudioDetailView, StudioUpdateView


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
]