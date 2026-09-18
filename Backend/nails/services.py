import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

from utils.coin_detector import get_pixel_to_mm_ratio
from utils.hand_detector import detect_hand
from ai.inference import MODEL
from utils.measurement import measure_nails
from utils.finger_identifier import identify_fingers
from utils.image_utils import draw_measurements
from utils.size_recommender import recommend_size


def run_pipeline(image_path, request=None, db_obj=None):
    """
    Executes the complete PressOn AI processing pipeline:
    1. Coin detection & verification (strict 27.0mm ₹10 reference).
    2. Hand landmark detection.
    3. YOLO nail segmentation.
    4. Nail measurements and finger identification (ONLY if ₹10 coin is verified).
    5. Recommended nail size calculation.
    6. Annotated visualization (green nail outlines + blue circular ₹10 coin boundary and label).
    
    Args:
        image_path (str): Absolute file path to the uploaded image.
        request (HttpRequest, optional): Current request to generate absolute URLs.
        db_obj (HandMeasurement, optional): Model instance to persist measurements.

    Returns:
        dict: Pipeline results containing:
            - coin_detected (bool)
            - coin_data (dict or None)
            - landmark_count (int)
            - landmarks (list)
            - identified_fingers (list of dicts with finger, recommended_size, width_mm, height_mm, raw_width, raw_height)
            - processed_file_path (str)
            - processed_image_url (str)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    import time
    t_pipeline = time.time()
    img_basename = os.path.basename(image_path)
    print(f"[PIPELINE] Starting PressOn AI processing pipeline for: {img_basename}", flush=True)

    # Output path for processed image inside media/processed/
    processed_dir = os.path.join(settings.MEDIA_ROOT, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    processed_filename = f"processed_{img_basename}"
    processed_file_path = os.path.join(processed_dir, processed_filename)

    coin_detected = False
    coin_data = None
    landmark_count = 0
    landmarks = []
    identified_fingers = []

    # 1. Coin Detection & Scale (Strict 27.0mm Rs. 10 reference validation)
    print("[PIPELINE] Step 1/6: Coin detection started (strict 27.0mm Rs. 10 reference)...", flush=True)
    t_coin = time.time()
    pixels_per_mm, coin_data = get_pixel_to_mm_ratio(image_path, real_coin_diameter_mm=27.0)
    coin_detected = (coin_data is not None)
    coin_dur = round(time.time() - t_coin, 2)
    if coin_detected:
        print(f"[PIPELINE] Step 1/6: Rs. 10 coin verified in {coin_dur}s (scale={pixels_per_mm:.2f} px/mm, radius={coin_data['radius']:.1f}px)", flush=True)
    else:
        print(f"[PIPELINE] Step 1/6: Rs. 10 coin NOT verified in {coin_dur}s", flush=True)

    # 2. Hand & Landmark Detection
    print("[PIPELINE] Step 2/6: Hand landmark detection started...", flush=True)
    t_hand = time.time()
    try:
        landmarks = detect_hand(image_path, processed_file_path)
        landmark_count = len(landmarks)
        print(f"[PIPELINE] Step 2/6: Hand detection completed in {time.time() - t_hand:.2f}s (landmarks={landmark_count})", flush=True)
    except Exception as hand_err:
        print(f"[PIPELINE] Step 2/6: Hand detection error in {time.time() - t_hand:.2f}s: {hand_err}", flush=True)
        landmarks = []
        landmark_count = 0

    # 3. Local YOLO Nail Segmentation (Strictly CPU)
    print("[PIPELINE] Step 3/6: YOLO nail segmentation started (CPU)...", flush=True)
    t_yolo = time.time()
    results = MODEL.predict(
        source=image_path,
        conf=0.30,
        save=False,
        verbose=False,
        device="cpu",
    )
    result_item = results[0]
    masks_count = len(result_item.masks.xy) if result_item.masks is not None else 0
    print(f"[PIPELINE] Step 3/6: YOLO segmentation completed in {time.time() - t_yolo:.2f}s (masks_detected={masks_count})", flush=True)

    # 4 & 5. Nail Measurements & Finger Identification ONLY if coin is verified
    if coin_detected:
        print(f"[PIPELINE] Step 4-5/6: Calculating nail measurements and mapping fingers...", flush=True)
        coin_diameter = coin_data["diameter_px"]
        if result_item.masks is not None:
            nail_measurements = measure_nails(result_item.masks.xy, coin_diameter=coin_diameter)
        else:
            nail_measurements = []

        if landmarks and nail_measurements:
            identified_fingers = identify_fingers(landmarks, nail_measurements)

        # Fallback naming if landmarks did not map to all detected nails
        if not identified_fingers and nail_measurements:
            default_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            if len(nail_measurements) == 4:
                default_names = ["Index", "Middle", "Ring", "Pinky"]
            elif len(nail_measurements) <= 3:
                default_names = ["Index", "Middle", "Ring"][:len(nail_measurements)]

            for i, nail in enumerate(nail_measurements):
                fname = default_names[i] if i < len(default_names) else f"Finger {i+1}"
                rec_size = recommend_size(nail["width_mm"])
                identified_fingers.append({
                    "finger": fname,
                    "width_mm": nail["width_mm"],
                    "height_mm": nail["height_mm"],
                    "width_px": nail["width_px"],
                    "height_px": nail["height_px"],
                    "raw_width": nail["width_px"],
                    "raw_height": nail["height_px"],
                    "size": rec_size,
                    "recommended_size": rec_size,
                })

        # Standardize finger dict fields
        for item in identified_fingers:
            if item.get("finger") == "Little":
                item["finger"] = "Pinky"
            item.setdefault("raw_width", item.get("width_px"))
            item.setdefault("raw_height", item.get("height_px"))
            item.setdefault("recommended_size", item.get("size"))

            # Round numeric metrics cleanly
            if "width_mm" in item and item["width_mm"] is not None:
                item["width_mm"] = round(float(item["width_mm"]), 2)
            if "height_mm" in item and item["height_mm"] is not None:
                item["height_mm"] = round(float(item["height_mm"]), 2)
            if "raw_width" in item and item["raw_width"] is not None:
                item["raw_width"] = round(float(item["raw_width"]), 2)
            if "raw_height" in item and item["raw_height"] is not None:
                item["raw_height"] = round(float(item["raw_height"]), 2)

        # Summary log for identified fingers
        finger_summary = [f"{item['finger']}:{item.get('recommended_size')}" for item in identified_fingers]
        print(f"[PIPELINE] Step 4-5/6: Identified and sized {len(identified_fingers)} fingers: {finger_summary}", flush=True)

        # Optional database persistence
        if db_obj is not None:
            for item in identified_fingers:
                db_name = item["finger"].lower()
                if db_name == "pinky":
                    db_name = "little"
                if hasattr(db_obj, db_name):
                    setattr(db_obj, db_name, item.get("width_mm"))
            if identified_fingers:
                sizes = [f"{item['finger']}:{item.get('recommended_size', item.get('size'))}" for item in identified_fingers]
                db_obj.recommended_size = ", ".join(sizes)[:30]
                db_obj.save()

        # 6. Annotate Image with Green Nails and BLUE ₹10 Coin Highlight
        print("[PIPELINE] Step 6/6: Rendering visual annotations (green nails + blue coin boundary)...", flush=True)
        base_img_path = processed_file_path if os.path.exists(processed_file_path) else image_path
        if result_item.masks is not None and nail_measurements:
            draw_measurements(base_img_path, result_item.masks.xy, nail_measurements, processed_file_path)

        if os.path.exists(processed_file_path):
            coin_img = cv2.imread(processed_file_path)
            if coin_img is not None:
                cx, cy = int(coin_data["center"][0]), int(coin_data["center"][1])
                cr = int(coin_data["radius"])

                # Draw clearly visible BLUE circle around the actual ₹10 coin boundary (BGR: 255, 0, 0)
                cv2.circle(coin_img, (cx, cy), cr, (255, 0, 0), 3, cv2.LINE_AA)

                # Add "₹10 Coin" blue label near the coin using PIL for crisp Unicode rendering
                try:
                    pil_img = Image.fromarray(cv2.cvtColor(coin_img, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_img)
                    label_text = "₹10 Coin"

                    try:
                        font = ImageFont.truetype("arial.ttf", 22)
                    except Exception:
                        font = ImageFont.load_default()

                    bbox = draw.textbbox((0, 0), label_text, font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

                    tx = max(10, min(coin_img.shape[1] - tw - 10, cx - tw // 2))
                    ty = cy - cr - th - 8
                    if ty < 10:
                        ty = cy + cr + 8

                    draw.rectangle((tx - 5, ty - 3, tx + tw + 5, ty + th + 3), fill=(255, 255, 255), outline=(0, 0, 255), width=1)
                    draw.text((tx, ty), label_text, font=font, fill=(0, 0, 255))

                    coin_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                except Exception as label_err:
                    print("[PIPELINE] Error drawing coin label:", label_err)
                    cv2.putText(coin_img, "10 Coin", (max(10, cx - 40), max(25, cy - cr - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

                cv2.imwrite(processed_file_path, coin_img)
    else:
        # When coin is not verified, do NOT generate fake scale or measurements
        nail_measurements = []
        identified_fingers = []
        print("[PIPELINE] Rs. 10 coin not verified. Sizing calculation aborted.", flush=True)

    # Generate processed image URL (absolute if request is provided, otherwise relative)
    if os.path.exists(processed_file_path):
        rel_url = f"{settings.MEDIA_URL}processed/{processed_filename}"
        if request is not None:
            processed_image_url = request.build_absolute_uri(rel_url)
        else:
            processed_image_url = rel_url
    else:
        processed_image_url = ""

    # Immediately release temporary OpenCV / NumPy / PyTorch memory buffers
    import gc
    gc.collect()

    dur_total = round(time.time() - t_pipeline, 2)
    print(f"[PIPELINE] Finished in {dur_total}s: coin_detected={coin_detected}, landmarks={landmark_count}, fingers={len(identified_fingers)}", flush=True)

    return {
        "coin_detected": coin_detected,
        "coin_data": coin_data,
        "landmark_count": landmark_count,
        "landmarks": landmarks,
        "identified_fingers": identified_fingers,
        "processed_file_path": processed_file_path,
        "processed_image_url": processed_image_url,
    }

