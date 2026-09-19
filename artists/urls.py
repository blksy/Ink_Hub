from django.urls import path

from .views import ArtistListView, ArtistDetailView,ArtistProfileUpdateView


app_name = "artists"

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist-list"),
    path("profile/edit/", ArtistProfileUpdateView.as_view(), name="artist-profile-edit"),
    path("<int:pk>/", ArtistDetailView.as_view(), name="artist-detail"),
]