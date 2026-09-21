from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView  
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .forms import ProfessionalProfileForm, PortfolioItemForm
from .models import ProfessionalProfile, PortfolioItem

class ProfessionalListView(ListView):
    model = ProfessionalProfile
    template_name = "professionals/professional_list.html"
    context_object_name = "professionals"


class ProfessionalDetailView(DetailView):
    model = ProfessionalProfile
    template_name = "professionals/professional_detail.html"
    context_object_name = "professional"


class ProfessionalProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfessionalProfile
    form_class = ProfessionalProfileForm
    template_name = "professionals/professional_profile_edit.html"

    def get_object(self, queryset=None):
        if self.request.user.role != self.request.user.Role.PROFESSIONAL:
            raise PermissionDenied("You do not have permission to edit this profile.")
        return self.request.user.professional_profile

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.pk},
        )


class PortfolioItemCreateView(LoginRequiredMixin, CreateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "professionals/portfolio_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.PROFESSIONAL:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.professional_profile = self.request.user.professional_profile

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )


class PortfolioItemUpdateView(LoginRequiredMixin, UpdateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "professionals/portfolio_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.PROFESSIONAL:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            professional_profile=self.request.user.professional_profile
        )

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )


class PortfolioItemDeleteView(LoginRequiredMixin, DeleteView):
    model = PortfolioItem
    template_name = "professionals/portfolio_item_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.PROFESSIONAL:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            professional_profile=self.request.user.professional_profile
        )

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )