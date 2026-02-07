from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from PIL import Image
import numpy as np
import cv2
import streamlit as st
from ultralytics import YOLO


WEIGHTS_PATH = "ml/best.pt"

# Map YOLO class names -> your app labels (edit after we read ewaste.yaml)
CLASS_TO_LABEL = {
    "CPU": "cpu",
    "RAM": "ram_stick",
    "USB_Drive": "flash_drive",
}


@st.cache_resource
def load_model() -> YOLO:
    return YOLO(WEIGHTS_PATH)

def run_model(image: Image.Image) -> Tuple[str, float, Optional[Image.Image], Optional[Dict[str, Any]]]:
    """
    Returns: (label, confidence, annotated_image, raw_detections)
    """
    model = load_model()

    # PIL -> OpenCV BGR
    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    results = model.predict(bgr, conf=0.25, verbose=False)
    r0 = results[0]

    raw: Dict[str, Any] = {"detections": []}

    if r0.boxes is None or len(r0.boxes) == 0:
        return "unknown", 0.0, None, raw

    # Pick highest-confidence detection as "the item"
    best_label = "unknown"
    best_conf = 0.0

    names = r0.names  # class id -> class name

    for box in r0.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        cls_name = str(names.get(cls_id, cls_id))

        mapped = CLASS_TO_LABEL.get(cls_name, "unknown")
        raw["detections"].append({
            "class_name": cls_name,
            "mapped_label": mapped,
            "confidence": conf,
        })

        if conf > best_conf:
            best_conf = conf
            best_label = mapped

    # Annotated image
    annotated_bgr = r0.plot()
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    annotated_pil = Image.fromarray(annotated_rgb)

    return best_label, best_conf, annotated_pil, raw
