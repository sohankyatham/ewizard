import random
from PIL import Image

LABELS = ["battery", "device", "cable", "unknown"]


def run_model(image: Image.Image):
    label = "ram_stick"
    conf = 0.95
    annotated = None
    raw = {"note": "hardcoded for MVP"}
    return label, conf, annotated, raw

