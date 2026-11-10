from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from common.validators import  MaxFileSizeValidator, validate_image_format, MaxImageDimensionsValidator


class ImageSizeValidatorTests(SimpleTestCase):

    def test_rejects_image_larger_than_5mb(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"x" * (6 * 1024 * 1024),
            content_type="image/jpeg",
        )

        validator =  MaxFileSizeValidator(5)

        with self.assertRaises(ValidationError):
            validator(image)


    def test_accepts_image_smaller_than_5mb(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"x" * (4 * 1024 * 1024),
            content_type="image/jpeg",
        )

        validator =  MaxFileSizeValidator(5)

        validator(image)

    def test_accepts_15mb_portfolio_image(self):
        image = SimpleUploadedFile(
            "portfolio.jpg",
            b"x" * (15 * 1024 * 1024),
            content_type="image/jpeg",
        )

        validator = MaxFileSizeValidator(20)

        validator(image)


class ImageFormatValidatorTests(SimpleTestCase):
    def test_accepts_png_image(self):
        buffer = BytesIO()

        image = Image.new("RGB", (100, 100), color="red")
        image.save(buffer, format="PNG")

        buffer.seek(0)

        validate_image_format(buffer)

    def test_recognizes_GIF_format(self):
        buffer = BytesIO()
        
        image = Image.new("RGB", (100, 100), color="red")
        image.save(buffer, format="GIF")
        
        buffer.seek(0)

        with self.assertRaises(ValidationError):
             validate_image_format(buffer)(buffer)

    def test_recognizes_false_JPEG(self):
        fake_image = SimpleUploadedFile(
            "fake.jpg",
            b"To nie jest prawdziwy obraz",
            content_type="image/jpeg",
        ) 

        with self.assertRaises(ValidationError):
            validate_image_format(fake_image)


class ImageDimensionsValidatorTests(SimpleTestCase):
    def test_accepts_image_within_max_range(self):
        buffer = BytesIO()
        
        image = Image.new("RGB", (1920, 1080), color="red")
        image.save(buffer, format="PNG")
        
        buffer.seek(0)
        
        validator = MaxImageDimensionsValidator(4096, 4096)

        validator(buffer)

    def test_rejects_image_larger_than_max_range(self):
        buffer = BytesIO()
                
        image = Image.new("RGB", (5000, 3000), color="red")
        image.save(buffer, format="PNG")
                
        buffer.seek(0)
                
        validator = MaxImageDimensionsValidator(4096, 4096)

        with self.assertRaises(ValidationError):
            validator(buffer)

    def test_rejects_image_with_one_value_larger_than_max_range(self):
        buffer = BytesIO()
                        
        image = Image.new("RGB", (3000, 5000), color="red")
        image.save(buffer, format="PNG")
                        
        buffer.seek(0)

        validator = MaxImageDimensionsValidator(4096, 4096)

        with self.assertRaises(ValidationError):
            validator(buffer)