from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView   
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .forms import ArtistProfileForm
from .models import ArtistProfile

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