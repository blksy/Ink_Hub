from django.urls import path

from .views import ProfessionalListView, ProfessionalDetailView, ProfessionalProfileUpdateView, PortfolioItemCreateView, PortfolioItemDeleteView, PortfolioItemUpdateView


app_name = "professionals"

urlpatterns = [
    path("", ProfessionalListView.as_view(), name="professional-list"),
    path("profile/edit/", ProfessionalProfileUpdateView.as_view(), name="professional-profile-edit"),
    path("portfolio/add/", PortfolioItemCreateView.as_view(), name="portfolio-item-create"),
    path("portfolio/<int:pk>/edit/",PortfolioItemUpdateView.as_view(),name="portfolio-item-update"),
    path("portfolio/<int:pk>/delete/", PortfolioItemDeleteView.as_view(), name="portfolio-item-delete"),
    path("<int:pk>/", ProfessionalDetailView.as_view(), name="professional-detail"),
]