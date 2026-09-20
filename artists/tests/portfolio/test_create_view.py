import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from artists.models import ArtistProfile, PortfolioItem, TattooStyle


User = get_user_model()