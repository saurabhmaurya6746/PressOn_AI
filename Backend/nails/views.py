import os
import base64
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.conf import settings

from .models import HandMeasurement
from utils.coin_detector import get_pixel_to_mm_ratio
from utils.hand_detector import detect_hand
from ai.inference import MODEL
from utils.measurement import measure_nails
from utils.finger_identifier import identify_fingers
from utils.image_utils import draw_measurements
from utils.size_recommender import recommend_size


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 15 * 1024 * 1024)


def home(request):

    if request.method == "POST":

        image = request.FILES.get("image")
        webcam_data = request.POST.get("webcam_image")

        if not image and not webcam_data:
            return render(request, "index.html", {
                "error_message": "Please select an image first."
            })

        # Case 1: Webcam captured photo
        if webcam_data:
            try:
                if ";base64," not in webcam_data:
                    return render(request, "index.html", {
                        "error_message": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
                    })

                fmt, imgstr = webcam_data.split(";base64,")
                raw_data = base64.b64decode(imgstr)

                if len(raw_data) > MAX_UPLOAD_SIZE:
                    return render(request, "index.html", {
                        "error_message": "Image is too large. Please upload a smaller image."
                    })

                import io
                from PIL import Image

                with Image.open(io.BytesIO(raw_data)) as test_img:
                    test_fmt = (test_img.format or "").upper()
                    if test_fmt not in ALLOWED_PIL_FORMATS:
                        return render(request, "index.html", {
                            "error_message": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                        })
                    test_img.verify()

                ext = "jpg" if test_fmt == "JPEG" else test_fmt.lower()
                image = ContentFile(raw_data, name=f"captured_hand.{ext}")

            except Exception as e:
                print("Webcam decode error:", e)
                return render(request, "index.html", {
                    "error_message": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
                })

        # Case 2: Uploaded image file
        elif image:
            # 1. Size check
            if image.size > MAX_UPLOAD_SIZE:
                return render(request, "index.html", {
                    "error_message": "Image is too large. Please upload a smaller image."
                })

            # 2. File extension check
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return render(request, "index.html", {
                    "error_message": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                })

            # 3. MIME type check
            content_type = getattr(image, "content_type", "").lower()
            if content_type and content_type not in ALLOWED_MIME_TYPES:
                return render(request, "index.html", {
                    "error_message": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                })

            # 4. Deep Image Content & Integrity Verification via Pillow
            try:
                from PIL import Image

                image.seek(0)
                with Image.open(image) as test_img:
                    test_fmt = (test_img.format or "").upper()
                    if test_fmt not in ALLOWED_PIL_FORMATS:
                        return render(request, "index.html", {
                            "error_message": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                        })
                    test_img.verify()
                image.seek(0)

            except Exception as img_err:
                print("Image verification error:", img_err)
                return render(request, "index.html", {
                    "error_message": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
                })

        if image:
            obj = HandMeasurement.objects.create(image=image)
            return redirect("result", pk=obj.id)

    return render(request, "index.html")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .services import run_pipeline


def result(request, pk):
    """
    Renders the HTML analysis report page for an uploaded hand measurement.
    Reuses the shared local AI processing pipeline.
    """
    obj = get_object_or_404(HandMeasurement, id=pk)

    try:
        original_image_url = obj.image.url
    except Exception:
        original_image_url = ""

    try:
        pipeline_res = run_pipeline(obj.image.path, request=request, db_obj=obj)
        coin_detected = pipeline_res["coin_detected"]
        landmark_count = pipeline_res["landmark_count"]
        identified_fingers = pipeline_res["identified_fingers"]
        processed_image_url = pipeline_res["processed_image_url"]
    except Exception as e:
        print("=" * 60)
        print("LOCAL AI INFERENCE ERROR")
        print(e)
        print("=" * 60)
        coin_detected = False
        landmark_count = 0
        identified_fingers = []
        processed_image_url = ""

    if not processed_image_url:
        processed_image_url = original_image_url

    context = {
        "obj": obj,
        "original_image_url": original_image_url,
        "processed_image": processed_image_url,
        "identified_fingers": identified_fingers,
        "landmark_count": landmark_count,
        "coin_detected": coin_detected,
    }

    return render(request, "result.html", context)


@csrf_exempt
@require_POST
def analyze_hand_api(request):
    """
    API Endpoint: POST /api/analyze/
    
    Accepts an uploaded hand image for precision press-on nail measurement and sizing analysis.
    
    Method: POST
    Content-Type: multipart/form-data
    Body:
        image (file, required): Uploaded hand image (JPG, JPEG, PNG, or WEBP, max 15MB).
        
    Success Response (HTTP 200):
        {
          "success": true,
          "coin_detected": true,
          "landmark_count": 21,
          "processed_image_url": "http://127.0.0.1:8000/media/processed/processed_xxx.png",
          "measurements": [
            {
              "finger": "Thumb",
              "recommended_size": "Size 9",
              "width_mm": 8.92,
              "height_mm": 11.86,
              "raw_width": 76.4,
              "raw_height": 101.7
            },
            ...
          ]
        }
        
    Error Responses:
        - HTTP 400 Bad Request: Missing image, unsupported format, oversized image, or corrupted image data.
        - HTTP 422 Unprocessable Entity: Valid image but ₹10 coin not verified, or hand/fingers not detectable.
            {
              "success": false,
              "coin_detected": false,
              "error": "Please upload an image with a clearly visible verified ₹10 coin."
            }
        - HTTP 500 Internal Server Error: Unexpected processing failure.
    """
    if "image" not in request.FILES:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Please provide an image file in the 'image' field."
        }, status=400)

    image_file = request.FILES["image"]

    # 1. File size check (Max 15MB)
    if image_file.size > MAX_UPLOAD_SIZE:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Image is too large. Please upload a smaller image."
        }, status=400)

    # 2. File extension check
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
        }, status=400)

    # 3. MIME type check
    content_type = getattr(image_file, "content_type", "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
        }, status=400)

    # 4. Deep Image Content & Integrity Verification via Pillow
    try:
        from PIL import Image
        image_file.seek(0)
        with Image.open(image_file) as test_img:
            test_fmt = (test_img.format or "").upper()
            if test_fmt not in ALLOWED_PIL_FORMATS:
                return JsonResponse({
                    "success": False,
                    "coin_detected": False,
                    "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                }, status=400)
            test_img.verify()
        image_file.seek(0)
    except Exception:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
        }, status=400)

    # 5. Persist upload and run the shared AI pipeline
    try:
        hand_obj = HandMeasurement.objects.create(image=image_file)
        pipeline_res = run_pipeline(hand_obj.image.path, request=request, db_obj=hand_obj)
    except Exception as pipe_err:
        print("[API PIPELINE ERROR]", pipe_err)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "An error occurred while processing the image. Please try again."
        }, status=500)

    # 6. Enforce strict ₹10 Coin Verification
    if not pipeline_res["coin_detected"]:
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Please upload an image with a clearly visible verified ₹10 coin."
        }, status=422)

    # 7. Enforce Hand / Finger Detection
    if pipeline_res["landmark_count"] == 0 and not pipeline_res["identified_fingers"]:
        return JsonResponse({
            "success": False,
            "coin_detected": True,
            "error": "No hand or fingers could be detected in the image. Please retake the photo with your hand clearly visible."
        }, status=422)

    # 8. Structure measurements array according to API specification
    measurements = []
    for item in pipeline_res["identified_fingers"]:
        raw_size = item.get("recommended_size", item.get("size", ""))
        if raw_size and raw_size != "Unknown" and not str(raw_size).lower().startswith("size"):
            rec_size_display = f"Size {raw_size}"
        else:
            rec_size_display = str(raw_size)

        measurements.append({
            "finger": item.get("finger", ""),
            "recommended_size": rec_size_display,
            "width_mm": item.get("width_mm", 0.0),
            "height_mm": item.get("height_mm", 0.0),
            "raw_width": item.get("raw_width", 0.0),
            "raw_height": item.get("raw_height", 0.0),
        })

    return JsonResponse({
        "success": True,
        "coin_detected": True,
        "landmark_count": pipeline_res["landmark_count"],
        "processed_image_url": pipeline_res["processed_image_url"],
        "measurements": measurements,
    }, status=200)
