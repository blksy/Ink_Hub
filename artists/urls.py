from django.urls import path

from .views import ProfessionalListView, ProfessionalDetailView, ProfessionalProfileUpdateView, PortfolioItemCreateView, PortfolioItemDeleteView, PortfolioItemUpdateView, ServiceCreateView, ServiceDeleteView, ServiceUpdateView


app_name = "professionals"

urlpatterns = [
    path("", ProfessionalListView.as_view(), name="professional-list"),
    path("profile/edit/", ProfessionalProfileUpdateView.as_view(), name="professional-profile-edit"),
    path("portfolio/add/", PortfolioItemCreateView.as_view(), name="portfolio-item-create"),
    path("portfolio/<int:pk>/edit/",PortfolioItemUpdateView.as_view(),name="portfolio-item-update"),
    path("portfolio/<int:pk>/delete/", PortfolioItemDeleteView.as_view(), name="portfolio-item-delete"),
    path("services/add/", ServiceCreateView.as_view(), name="service-create"),
    path("services/<int:pk>/edit/", ServiceUpdateView.as_view(), name="service-update"),
    path("services/<int:pk>/delete/", ServiceDeleteView.as_view(), name="service-delete"),
    path("<int:pk>/", ProfessionalDetailView.as_view(), name="professional-detail"),
]