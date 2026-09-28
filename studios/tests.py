from django.test import TestCase

from studios.models import Studio


class StudioModelTests(TestCase):
    def test_studio_string_representation_returns_name(self):
        studio = Studio.objects.create(
            name="Gentlemen Barber Poznań",
            location="Poznań",
        )

        self.assertEqual(str(studio), "Gentlemen Barber Poznań")