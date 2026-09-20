from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView  
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .forms import ArtistProfileForm, PortfolioItemForm
from .models import ArtistProfile, PortfolioItem

class ArtistListView(ListView):
    model = ArtistProfile
    template_name = "artists/artist_list.html"
    context_object_name = "artists"


class ArtistDetailView(DetailView):
    model = ArtistProfile
    template_name = "artists/artist_detail.html"
    context_object_name = "artist"


class ArtistProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ArtistProfile
    form_class = ArtistProfileForm
    template_name = "artists/artist_profile_edit.html"

    def get_object(self, queryset=None):
        if self.request.user.role != self.request.user.Role.ARTIST:
            raise PermissionDenied("You do not have permission to edit this profile.")
        return self.request.user.artist_profile

    def get_success_url(self):
        return reverse(
            "artists:artist-detail",
            kwargs={"pk": self.object.pk},
        )


class PortfolioItemCreateView(LoginRequiredMixin, CreateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "artists/portfolio_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.ARTIST:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.artist_profile = self.request.user.artist_profile

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "artists:artist-detail",
            kwargs={"pk": self.object.artist_profile.pk},
        )


class PortfolioItemUpdateView(LoginRequiredMixin, UpdateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = "artists/portfolio_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.ARTIST:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            artist_profile=self.request.user.artist_profile
        )

    def get_success_url(self):
        return reverse(
            "artists:artist-detail",
            kwargs={"pk": self.object.artist_profile.pk},
        )


class PortfolioItemDeleteView(LoginRequiredMixin, DeleteView):
    model = PortfolioItem
    template_name = "artists/portfolio_item_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role != request.user.Role.ARTIST:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            artist_profile=self.request.user.artist_profile
        )

    def get_success_url(self):
        return reverse(
            "artists:artist-detail",
            kwargs={"pk": self.object.artist_profile.pk},
        )