import random
from PIL import Image

LABELS = ["battery", "device", "cable", "unknown"]

def run_model(image: Image.Image):
    label = random.choice(LABELS)
    conf = random.uniform(0.7, 0.99) if label != "unknown" else random.uniform(0.3, 0.6)
    return label, conf
