import os
import threading
from utils.measurement import measure_nails
from utils.image_utils import draw_measurements

WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights", "best.pt")
_model = None
_model_lock = threading.Lock()


def get_model():
    """Thread-safe lazy singleton loader for YOLOv11 segmentation model.
    Defers PyTorch & weights loading until first inference call to prevent Django startup OOM.
    """
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                import time
                t_load = time.time()
                print("[AI] 3/5 Model loading started: initializing PyTorch CPU runtime and YOLOv11...")
                try:
                    import torch
                    torch.set_num_threads(2)
                    if hasattr(torch, "set_num_interop_threads"):
                        torch.set_num_interop_threads(1)
                except Exception as th_err:
                    print(f"[AI] PyTorch thread config note: {th_err}")

                from ultralytics import YOLO
                resolved_path = WEIGHTS_PATH if os.path.exists(WEIGHTS_PATH) else "ai/weights/best.pt"
                _model = YOLO(resolved_path)
                print(f"[AI] 3/5 Model loading completed in {time.time() - t_load:.2f}s (YOLOv11 ready on CPU)")
    return _model



class _LazyModelProxy:
    """Proxy object preserving full backward compatibility for:
    from ai.inference import MODEL
    while deferring heavy PyTorch / YOLO initialization until first inference call.
    """
    def __getattr__(self, name):
        return getattr(get_model(), name)

    def __call__(self, *args, **kwargs):
        return get_model()(*args, **kwargs)


MODEL = _LazyModelProxy()


def predict_nails(image_path, coin_diameter=100.0):
    results = get_model().predict(
        source=image_path,
        conf=0.30,
        save=False,
        verbose=False,
        device="cpu",
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