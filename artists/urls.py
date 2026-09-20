from django.urls import path

from .views import ArtistListView, ArtistDetailView, ArtistProfileUpdateView, PortfolioItemCreateView, PortfolioItemDeleteView, PortfolioItemUpdateView


app_name = "artists"

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist-list"),
    path("profile/edit/", ArtistProfileUpdateView.as_view(), name="artist-profile-edit"),
    path("portfolio/add/", PortfolioItemCreateView.as_view(), name="portfolio-item-create"),
    path("portfolio/<int:pk>/edit/",PortfolioItemUpdateView.as_view(),name="portfolio-item-update"),
    path("portfolio/<int:pk>/delete/", PortfolioItemDeleteView.as_view(), name="portfolio-item-delete"),
    path("<int:pk>/", ArtistDetailView.as_view(), name="artist-detail"),
]