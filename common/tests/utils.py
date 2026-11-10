
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_image(
    name="test.png",
    width=100,
    height=100,
    color="white",
):
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
        color=color,
    )

    image.save(buffer, format="PNG")

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type="image/png",
    )
