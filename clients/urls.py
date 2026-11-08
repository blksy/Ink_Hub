from django.urls import path

from clients.views import (
    ClientProfileDetailView, 
    ClientProfileUpdateView, 
    ClientProfileActivateView
)

app_name = "clients"

urlpatterns = [
    path(
        "profile/",
        ClientProfileDetailView.as_view(),
        name="client-profile",
    ),

    path(
        "profile/edit/",
        ClientProfileUpdateView.as_view(),
        name="client-profile-update"
    ),

     path(
        "profile/activate/",
        ClientProfileActivateView.as_view(),
        name="client-profile-activate",
    ),
]