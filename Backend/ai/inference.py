import os
from ultralytics import YOLO
from utils.measurement import measure_nails
from utils.image_utils import draw_measurements

WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights", "best.pt")
MODEL = YOLO(WEIGHTS_PATH if os.path.exists(WEIGHTS_PATH) else "ai/weights/best.pt")


def predict_nails(image_path, coin_diameter=100.0):
    results = MODEL.predict(
        source=image_path,
        conf=0.30,
        save=False,
        verbose=False
    )

    result = results[0]

    # Agar koi mask detect nahi hua toh empty dict ya validation handle karein
    if result.masks is None:
        return {
            "measurements": [],
            "processed_image": None,
            "result": result
        }

    # Measurements calculate karna
    measurements = measure_nails(result.masks.xy, coin_diameter=coin_diameter)

    # Output path set karna (media/processed/ folder ke andar)
    output_path = os.path.join(
        "media",
        "processed",
        os.path.basename(image_path)
    )
    
    # Make sure ki output directory exists karti ho (error se bachne ke liye)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Image par measurements draw karke save karna
    draw_measurements(
        image_path,
        result.masks.xy,
        measurements,
        output_path
    )

    # Final response return karna
    return {
        "measurements": measurements,
        "processed_image": output_path
    }