from django.views.generic import ( 
    ListView, 
    DetailView, 
    UpdateView, 
    DeleteView, 
    CreateView,
)  

from .forms import ( 
    ProfessionalProfileForm, 
    PortfolioItemForm, 
    ServiceForm,
)

from django.urls import reverse, reverse_lazy
from .mixins import ProfessionalRequiredMixin
from .models import ProfessionalProfile, PortfolioItem, Service

class ProfessionalListView(ListView):
    model = ProfessionalProfile
    template_name = "professionals/professional_list.html"
    context_object_name = "professionals"


class ProfessionalDetailView(DetailView):
    model = ProfessionalProfile
    template_name = "professionals/professional_detail.html"
    context_object_name = "professional"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context["services"] = self.object.services.filter(
            is_active=True
        )
    
        return context


class ProfessionalProfileUpdateView(ProfessionalRequiredMixin, UpdateView):
    model = ProfessionalProfile
    form_class = ProfessionalProfileForm
    template_name = "professionals/professional_profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user.professional_profile

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.pk},
        )


class PortfolioItemCreateView(ProfessionalRequiredMixin, CreateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "professionals/portfolio_item_form.html"

    def form_valid(self, form):
        form.instance.professional_profile = self.request.user.professional_profile

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )


class PortfolioItemUpdateView(ProfessionalRequiredMixin, UpdateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "professionals/portfolio_item_form.html"

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            professional_profile=self.request.user.professional_profile
        )

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )


class PortfolioItemDeleteView(ProfessionalRequiredMixin, DeleteView):
    model = PortfolioItem
    template_name = "professionals/portfolio_item_confirm_delete.html"

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            professional_profile=self.request.user.professional_profile
        )

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.professional_profile.pk},
        )


class ServiceCreateView(ProfessionalRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "professionals/service_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["professional"] = self.request.user.professional_profile
        return kwargs

    def form_valid(self, form):
        form.instance.professional = self.request.user.professional_profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "professionals:professional-detail",
            kwargs={
                "pk": self.request.user.professional_profile.pk,
            },
        )


class ServiceUpdateView(ProfessionalRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "professionals/service_form.html"

    def get_queryset(self):
        return Service.objects.filter(
            professional=self.request.user.professional_profile
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["professional"] = self.request.user.professional_profile
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "professionals:professional-detail",
            kwargs={
                "pk": self.request.user.professional_profile.pk,
            },
        )


class ServiceDeleteView(ProfessionalRequiredMixin, DeleteView):
    model = Service
    template_name = "professionals/service_confirm_delete.html"

    def get_queryset(self):
        return Service.objects.filter(
            professional=self.request.user.professional_profile
        )

    def get_success_url(self):
        return reverse_lazy(
            "professionals:professional-detail",
            kwargs={
                "pk": self.request.user.professional_profile.pk,
            },
        )