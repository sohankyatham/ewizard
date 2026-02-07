import random
from PIL import Image

LABELS = ["battery", "device", "cable", "unknown"]

def run_model(image: Image.Image):
    label = random.choice(LABELS)
    conf = random.uniform(0.7, 0.99) if label != "unknown" else random.uniform(0.3, 0.6)

    annotated = None  # later: return an image with YOLO boxes
    raw = None        # later: return raw YOLO detections for dev mode
    return label, conf, annotated, raw
