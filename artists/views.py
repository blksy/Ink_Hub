from django.db import transaction
from django.shortcuts import redirect
from django.db.models import Prefetch

from django.views.generic import ( 
    ListView, 
    DetailView, 
    UpdateView, 
    DeleteView, 
    CreateView,
)  

from .forms import ( 
    ProfessionalProfileForm, 
    UserPersonalDataForm,
    PortfolioItemForm, 
    ServiceForm,
)

from studios.mixins import StudioManagementRequiredMixin
from django.urls import reverse, reverse_lazy
from .mixins import ProfessionalRequiredMixin
from .models import ProfessionalProfile, PortfolioItem, Service
from studios.models import EmployeeService, StudioMembership



class ProfessionalListView(ListView):
    model = ProfessionalProfile
    template_name = "professionals/professional_list.html"
    context_object_name = "professionals"

    def get_queryset(self):
        active_memberships = (
            StudioMembership.objects.filter(
                status=StudioMembership.Status.ACTIVE,
            )
            .select_related("studio")
        )

        return (
            ProfessionalProfile.objects
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "studio_memberships",
                    queryset=active_memberships,
                    to_attr="active_memberships",
                )
            )
        )


class ProfessionalDetailView(DetailView):
    model = ProfessionalProfile
    template_name = "professionals/professional_detail.html"
    context_object_name = "professional"

    def get_queryset(self):
        return ProfessionalProfile.objects.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        memberships = (
            StudioMembership.objects.filter(
                professional=self.object,
                status=StudioMembership.Status.ACTIVE,
            )
            .select_related("studio")
            .prefetch_related("studio__categories")
        )

        employee_services = (
            EmployeeService.objects.filter(
                membership__professional=self.object,
                membership__status=StudioMembership.Status.ACTIVE,
            )
            .select_related(
                "service",
                "service__category",
                "membership__studio",
            )
        )

        is_owner = (
            self.request.user.is_authenticated
            and self.object.user_id == self.request.user.pk
        )

        if not is_owner:
            employee_services = employee_services.filter(
                is_active=True,
                service__is_active=True,
            )

        context["memberships"] = memberships
        context["employee_services"] = employee_services
        context["is_profile_owner"] = is_owner

        return context


class ProfessionalProfileUpdateView(ProfessionalRequiredMixin, UpdateView):
    model = ProfessionalProfile
    form_class = ProfessionalProfileForm
    template_name = "professionals/professional_profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user.professional_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "user_form" not in context:
            context["user_form"] = UserPersonalDataForm(
                instance=self.request.user,
                prefix="user",
            )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        profile_form = self.get_form()

        user_form = UserPersonalDataForm(
            request.POST,
            instance=request.user,
            prefix="user",
        )

        if profile_form.is_valid() and user_form.is_valid():
            with transaction.atomic():
                user_form.save()
                self.object = profile_form.save()

            return redirect(self.get_success_url())

        return self.render_to_response(
            self.get_context_data(
                form=profile_form,
                user_form=user_form,
            )
        )

    def get_success_url(self):
        return reverse(
            "professionals:professional-detail",
            kwargs={"pk": self.object.pk},
        )


class PortfolioItemCreateView(ProfessionalRequiredMixin, CreateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "professionals/portfolio_item_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["professional"] = self.request.user.professional_profile
        return kwargs

    def form_valid(self, form):
        form.instance.professional_profile = (
            self.request.user.professional_profile
        )
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["professional"] = self.request.user.professional_profile
        return kwargs

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


class ServiceCreateView(ProfessionalRequiredMixin, StudioManagementRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "professionals/service_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["studio"] = self.studio
        return kwargs

    def get_success_url(self):
        return reverse(
            "studios:studio-detail",
            kwargs={"pk": self.studio.pk},
        )


class ServiceUpdateView(ProfessionalRequiredMixin, StudioManagementRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "professionals/service_form.html"

    def get_queryset(self):
        return Service.objects.filter(
            studio=self.studio
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["studio"] = self.studio
        return kwargs

    def get_success_url(self):
            return reverse(
                "studios:studio-detail",
                kwargs={"pk": self.studio.pk},
            )


class ServiceDeleteView(ProfessionalRequiredMixin, StudioManagementRequiredMixin, DeleteView):
    model = Service
    template_name = "professionals/service_confirm_delete.html"

    def get_queryset(self):
        return Service.objects.filter(
            studio=self.studio,
        )

    def get_success_url(self):
            return reverse(
                "studios:studio-detail",
                kwargs={"pk": self.studio.pk},
           )