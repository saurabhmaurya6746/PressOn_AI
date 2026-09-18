from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image


def create_test_image(format_name):
    """Helper to generate small in-memory valid images in various formats."""
    file_obj = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image.save(file_obj, format=format_name)
    file_obj.seek(0)
    return file_obj.read()


class ImageUploadValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home")

    def test_01_valid_jpg_upload(self):
        """Valid JPG upload succeeds and redirects to result."""
        img_bytes = create_test_image("JPEG")
        uploaded = SimpleUploadedFile("hand_sample.jpg", img_bytes, content_type="image/jpeg")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/result/"))

    def test_02_valid_jpeg_upload(self):
        """Valid JPEG upload succeeds and redirects to result."""
        img_bytes = create_test_image("JPEG")
        uploaded = SimpleUploadedFile("hand_sample.jpeg", img_bytes, content_type="image/jpeg")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/result/"))

    def test_03_valid_png_upload(self):
        """Valid PNG upload succeeds and redirects to result."""
        img_bytes = create_test_image("PNG")
        uploaded = SimpleUploadedFile("hand_sample.png", img_bytes, content_type="image/png")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/result/"))

    def test_04_valid_webp_upload(self):
        """Valid WEBP upload succeeds and redirects to result."""
        img_bytes = create_test_image("WEBP")
        uploaded = SimpleUploadedFile("hand_sample.webp", img_bytes, content_type="image/webp")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/result/"))

    def test_05_unsupported_pdf_upload(self):
        """Uploading a PDF is rejected with exact format error message."""
        fake_pdf = b"%PDF-1.4 test content fake pdf"
        uploaded = SimpleUploadedFile("document.pdf", fake_pdf, content_type="application/pdf")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context.get("error_message"),
            "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
        )

    def test_06_unsupported_gif_upload(self):
        """Uploading a GIF is rejected with exact format error message."""
        fake_gif = b"GIF89a" + b"\x00" * 20
        uploaded = SimpleUploadedFile("animated.gif", fake_gif, content_type="image/gif")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context.get("error_message"),
            "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
        )

    def test_07_corrupted_or_disguised_file(self):
        """File with .jpg extension but corrupted/non-image data is rejected."""
        garbage_bytes = b"This is definitely not a valid JPEG image file header!"
        uploaded = SimpleUploadedFile("corrupted.jpg", garbage_bytes, content_type="image/jpeg")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context.get("error_message"),
            "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
        )

    def test_08_empty_submission(self):
        """Submitting without selecting a file or camera image displays error."""
        response = self.client.post(self.home_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context.get("error_message"),
            "Please select an image first."
        )

    def test_09_oversized_file(self):
        """File exceeding 15MB is rejected with size error."""
        oversized_data = b"0" * (15 * 1024 * 1024 + 1024)
        uploaded = SimpleUploadedFile("huge.jpg", oversized_data, content_type="image/jpeg")
        response = self.client.post(self.home_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context.get("error_message"),
            "Image is too large. Please upload a smaller image."
        )


import os
from django.conf import settings
import json


class AnalyzeHandApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_url = reverse("api_analyze")
        self.valid_10_path = os.path.join(settings.BASE_DIR, "media", "uploads", "test_valid_10.png")
        self.no_coin_path = os.path.join(settings.BASE_DIR, "media", "uploads", "test_hand_0002801.jpg")

    def test_a_valid_jpg_with_verified_coin(self):
        """A. Valid JPG with verified ₹10 coin returns 200 with complete sizing schema."""
        with Image.open(self.valid_10_path) as img:
            rgb_img = img.convert("RGB")
            buf = io.BytesIO()
            rgb_img.save(buf, format="JPEG")
            jpg_bytes = buf.getvalue()

        uploaded = SimpleUploadedFile("hand_coin.jpg", jpg_bytes, content_type="image/jpeg")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["coin_detected"])
        self.assertGreaterEqual(data["landmark_count"], 0)
        self.assertTrue(data["processed_image_url"])
        self.assertIsInstance(data["measurements"], list)
        self.assertGreater(len(data["measurements"]), 0)

        # Validate measurement schema item
        item = data["measurements"][0]
        self.assertIn("finger", item)
        self.assertIn("recommended_size", item)
        self.assertIn("width_mm", item)
        self.assertIn("height_mm", item)
        self.assertIn("raw_width", item)
        self.assertIn("raw_height", item)

    def test_b_valid_png_with_verified_coin(self):
        """B. Valid PNG with verified ₹10 coin returns 200 with complete sizing schema."""
        with open(self.valid_10_path, "rb") as f:
            png_bytes = f.read()

        uploaded = SimpleUploadedFile("hand_coin.png", png_bytes, content_type="image/png")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["coin_detected"])
        self.assertTrue(data["processed_image_url"])
        self.assertGreater(len(data["measurements"]), 0)

    def test_c_valid_webp_with_verified_coin(self):
        """C. Valid WEBP with verified ₹10 coin returns 200 with complete sizing schema."""
        with Image.open(self.valid_10_path) as img:
            rgb_img = img.convert("RGB")
            buf = io.BytesIO()
            rgb_img.save(buf, format="WEBP")
            webp_bytes = buf.getvalue()

        uploaded = SimpleUploadedFile("hand_coin.webp", webp_bytes, content_type="image/webp")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["coin_detected"])
        self.assertTrue(data["processed_image_url"])
        self.assertGreater(len(data["measurements"]), 0)

    def test_d_missing_image(self):
        """D. Missing image field returns 400 with descriptive error."""
        response = self.client.post(self.api_url, {})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertFalse(data["coin_detected"])
        self.assertEqual(data["error"], "Please provide an image file in the 'image' field.")

    def test_e_unsupported_file(self):
        """E. Unsupported file format (PDF) returns 400 with format error."""
        fake_pdf = b"%PDF-1.4 sample file content"
        uploaded = SimpleUploadedFile("report.pdf", fake_pdf, content_type="application/pdf")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertFalse(data["coin_detected"])
        self.assertEqual(data["error"], "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image.")

    def test_f_corrupted_image(self):
        """F. Corrupted / disguised file returns 400 with unreadable image error."""
        garbage_bytes = b"NOT_A_VALID_IMAGE_FILE_CONTENT_AT_ALL"
        uploaded = SimpleUploadedFile("broken.jpg", garbage_bytes, content_type="image/jpeg")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertFalse(data["coin_detected"])
        self.assertEqual(data["error"], "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image.")

    def test_g_image_without_verified_coin(self):
        """G. Image without verified ₹10 coin returns 422 with coin verification error."""
        with open(self.no_coin_path, "rb") as f:
            no_coin_bytes = f.read()

        uploaded = SimpleUploadedFile("hand_no_coin.jpg", no_coin_bytes, content_type="image/jpeg")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertFalse(data["coin_detected"])
        self.assertEqual(data["error"], "Please upload an image with a clearly visible verified ₹10 coin.")

    def test_h_valid_image_with_no_detectable_hand(self):
        """H. Valid image where coin is verified but no hand/fingers detectable returns 422."""
        # Create a test image with coin pasted on blank white background (no hand or fingers)
        with Image.open(self.valid_10_path) as img:
            coin_crop = img.crop((910, 380, 1135, 605))
            canvas = Image.new("RGB", (1200, 1200), color=(255, 255, 255))
            canvas.paste(coin_crop, (200, 200))
            buf = io.BytesIO()
            canvas.save(buf, format="PNG")
            coin_only_bytes = buf.getvalue()

        uploaded = SimpleUploadedFile("coin_only.png", coin_only_bytes, content_type="image/png")
        response = self.client.post(self.api_url, {"image": uploaded})
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_i_cors_headers(self):
        """I. CORS headers are returned for allowed origins."""
        response = self.client.options(
            self.api_url,
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")

    def test_j_production_cors_headers(self):
        """J. CORS headers are returned for deployed production frontend origin."""
        response = self.client.options(
            self.api_url,
            HTTP_ORIGIN="https://aura-nails-ad6m.onrender.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "https://aura-nails-ad6m.onrender.com")


from utils.size_recommender import recommend_size, SIZE_CHART


class SizeRecommenderTests(TestCase):
    """Unit tests for the authoritative Press-On AI nail size mapping (Sizes 0 to 8)."""

    def test_approved_exact_nominal_sizes(self):
        """Tests that nominal nail widths map to correct sizes."""
        self.assertEqual(recommend_size(18.5), "0")
        self.assertEqual(recommend_size(17.0), "0")
        self.assertEqual(recommend_size(16.0), "1")
        self.assertEqual(recommend_size(15.0), "2")
        self.assertEqual(recommend_size(14.0), "3")
        self.assertEqual(recommend_size(13.0), "4")
        self.assertEqual(recommend_size(12.0), "5")
        self.assertEqual(recommend_size(11.0), "6")
        self.assertEqual(recommend_size(10.0), "7")
        self.assertEqual(recommend_size(9.0), "8")

    def test_approved_midpoint_intervals(self):
        """Tests interval boundaries and values between nominal points."""
        self.assertEqual(recommend_size(17.5), "0")
        self.assertEqual(recommend_size(16.5), "0")
        self.assertEqual(recommend_size(15.5), "1")
        self.assertEqual(recommend_size(14.5), "2")
        self.assertEqual(recommend_size(13.5), "3")
        self.assertEqual(recommend_size(12.5), "4")
        self.assertEqual(recommend_size(11.5), "5")
        self.assertEqual(recommend_size(10.5), "6")
        self.assertEqual(recommend_size(9.5), "7")
        self.assertEqual(recommend_size(9.2), "8")

    def test_outside_supported_range(self):
        """Tests that widths below 9.0 mm return 'Outside supported size range' without inventing Size 9."""
        self.assertEqual(recommend_size(6.68), "Outside supported size range")
        self.assertEqual(recommend_size(8.99), "Outside supported size range")
        self.assertEqual(recommend_size(0.0), "Outside supported size range")
        self.assertEqual(recommend_size(-2.5), "Outside supported size range")

    def test_invalid_and_none_values(self):
        """Tests handling of None and invalid inputs."""
        self.assertEqual(recommend_size(None), "Unknown")
        self.assertEqual(recommend_size("invalid"), "Unknown")



