import os
import time
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import HandMeasurement
from .services import run_pipeline


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 15 * 1024 * 1024)


def api_health(request):
    """
    API Health and Root Information Endpoint.
    Returns operational status and active API endpoint information.
    """
    return JsonResponse({
        "status": "healthy",
        "service": "PressOn AI Measurement API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze/",
            "health": "/api/health/"
        }
    }, status=200)


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
              "recommended_size": "Outside supported size range",
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
    import time
    t_api_start = time.time()
    origin = request.headers.get("Origin", "None")
    client_ip = request.META.get("REMOTE_ADDR", "unknown")
    print(f"[API] 1/7 Request received: method=POST, origin={origin}, client_ip={client_ip}", flush=True)

    if "image" not in request.FILES:
        print("[API] Request rejected: missing 'image' field in multipart form data", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Please provide an image file in the 'image' field."
        }, status=400)

    image_file = request.FILES["image"]
    file_size_kb = round(image_file.size / 1024, 2)

    # 1. File size check (Max 15MB)
    if image_file.size > MAX_UPLOAD_SIZE:
        print(f"[API] Request rejected: image too large ({file_size_kb} KB > {MAX_UPLOAD_SIZE // 1024} KB)", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Image is too large. Please upload a smaller image."
        }, status=400)

    # 2. File extension check
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        print(f"[API] Request rejected: invalid file extension '{ext}'", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
        }, status=400)

    # 3. MIME type check
    content_type = getattr(image_file, "content_type", "").lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        print(f"[API] Request rejected: invalid MIME type '{content_type}'", flush=True)
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
            img_width, img_height = test_img.size
            if test_fmt not in ALLOWED_PIL_FORMATS:
                print(f"[API] Request rejected: PIL format '{test_fmt}' not allowed", flush=True)
                return JsonResponse({
                    "success": False,
                    "coin_detected": False,
                    "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
                }, status=400)
            test_img.verify()
        image_file.seek(0)
        print(f"[API] 2/7 Image validation completed: filename='{image_file.name}', format={test_fmt}, size={file_size_kb} KB, dimensions={img_width}x{img_height}", flush=True)
    except Exception as img_err:
        print(f"[API] Image verification error: {img_err}", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
        }, status=400)

    # 5. Persist upload and run the shared AI pipeline
    try:
        hand_obj = HandMeasurement.objects.create(image=image_file)
        print(f"[API] 3/7 Database record created (id={hand_obj.id}). Invoking AI pipeline...", flush=True)
        pipeline_res = run_pipeline(hand_obj.image.path, request=request, db_obj=hand_obj)
    except Exception as pipe_err:
        print("[API PIPELINE ERROR]", pipe_err, flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "An error occurred while processing the image. Please try again."
        }, status=500)

    # 6. Enforce strict ₹10 Coin Verification
    if not pipeline_res["coin_detected"]:
        print("[API] 4/7 Verification result: Rs. 10 coin not verified (returning status 422)", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": False,
            "error": "Please upload an image with a clearly visible verified ₹10 coin."
        }, status=422)

    # 7. Enforce Hand / Finger Detection
    if pipeline_res["landmark_count"] == 0 and not pipeline_res["identified_fingers"]:
        print("[API] 5/7 Verification result: hand/fingers not detected (returning status 422)", flush=True)
        return JsonResponse({
            "success": False,
            "coin_detected": True,
            "error": "No hand or fingers could be detected in the image. Please retake the photo with your hand clearly visible."
        }, status=422)

    # 8. Structure measurements array according to API specification
    measurements = []
    for item in pipeline_res["identified_fingers"]:
        raw_size = item.get("recommended_size", item.get("size", ""))
        raw_size_str = str(raw_size).strip()
        if raw_size_str.isdigit():
            rec_size_display = f"Size {raw_size_str}"
        elif raw_size_str.lower().startswith("size"):
            rec_size_display = raw_size_str
        else:
            rec_size_display = raw_size_str

        width_mm = item.get("width_mm", 0.0)
        height_mm = item.get("height_mm", 0.0)
        raw_w = item.get("raw_width", item.get("width_px", 0.0))
        raw_h = item.get("raw_height", item.get("height_px", 0.0))

        # Log calculation pipeline
        print(f"[SIZE CALC] Finger={item.get('finger')}: raw_width={raw_w}px -> calibrated_width={width_mm}mm -> mapped_size={rec_size_display}", flush=True)

        measurements.append({
            "finger": item.get("finger", ""),
            "recommended_size": rec_size_display,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "raw_width": raw_w,
            "raw_height": raw_h,
        })

    elapsed_api = round(time.time() - t_api_start, 2)
    print(f"[API] 6/7 Measurements formatted: {len(measurements)} fingers ready", flush=True)
    print(f"[API] 7/7 Response generated: status=200, elapsed={elapsed_api}s, coin_detected=True, landmarks={pipeline_res['landmark_count']}, measurements_count={len(measurements)}", flush=True)

    return JsonResponse({
        "success": True,
        "coin_detected": True,
        "landmark_count": pipeline_res["landmark_count"],
        "processed_image_url": pipeline_res["processed_image_url"],
        "measurements": measurements,
    }, status=200)
