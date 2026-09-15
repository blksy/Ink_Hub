from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import ArtistProfile


class ArtistListView(ListView):
    model = ArtistProfile
    template_name = "artists/artist_list.html"
    context_object_name = "artists"

class ArtistDetailView(DetailView):
    model = ArtistProfile
    template_name = "artists/artist_detail.html"
    context_object_name = "artist"