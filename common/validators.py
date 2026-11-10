from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


def validate_image_format(image):
    allowed_formats = {"JPEG", "PNG", "WEBP"}

    try:
        image.seek(0)

        with Image.open(image) as img:
            image_format = img.format
            img.verify()

        if image_format not in allowed_formats:
            raise ValidationError(
                "Dozwolone formaty zdjęć: JPEG, PNG, WebP."
            )

    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError(
            "Przesłany plik nie jest prawidłowym obrazem."
        )

    finally:
        image.seek(0)

@deconstructible
class MaxFileSizeValidator:
    def __init__(self, max_mb=5):
        self.max_mb = max_mb

    def __call__(self, image):
        max_bytes = self.max_mb * 1024 * 1024

        if image.size > max_bytes:
            raise ValidationError(
                f"Plik nie może przekraczać {self.max_mb} MB."
            )

    def __eq__(self, other):
        return (
            isinstance(other, MaxFileSizeValidator)
            and self.max_mb == other.max_mb
        )


@deconstructible
class MaxImageDimensionsValidator:
    def __init__(self, max_width=4096, max_height=4096):
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, image):
        try:
            image.seek(0)

            with Image.open(image) as img:
                width, height = img.size

            if width > self.max_width or height > self.max_height:
                raise ValidationError(
                    f"Maksymalne wymiary obrazu to "
                    f"{self.max_width} × {self.max_height} pikseli."
                )

        except (UnidentifiedImageError, OSError, ValueError):
            raise ValidationError(
                "Nie można odczytać wymiarów obrazu."
            )

        finally:
            image.seek(0)

    def __eq__(self, other):
        return (
            isinstance(other, MaxImageDimensionsValidator)
            and self.max_width == other.max_width
            and self.max_height == other.max_height
        )