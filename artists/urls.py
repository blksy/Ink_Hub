from django.urls import path

from .views import ArtistListView, ArtistDetailView


app_name = "artists"

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist-list"),
    path("<int:pk>/", ArtistDetailView.as_view(), name="artist-detail"),
]