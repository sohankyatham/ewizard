from ultralytics import YOLO
import cv2
from gpiozero import Servo
from time import sleep

# --------------------
# Servo setup (ONE SERVO)
# --------------------
SERVO_GPIO = 18  # GPIO pin for the servo

servo = Servo(
    SERVO_GPIO,
    min_pulse_width=0.5 / 1000,   # 0.5 ms
    max_pulse_width=2.5 / 1000    # 2.5 ms
)

def angle_to_value(angle):
    """
    Convert angle (0–180°) to gpiozero Servo value (-1 to +1)
    """
    angle = max(0, min(180, angle))
    return (angle / 90.0) - 1.0

def move_servo(angle):
    servo.value = angle_to_value(angle)
    sleep(0.15)  # give servo time to move

# Mapping from YOLO labels → servo angles
ANGLE_MAP = {
    "USB_Drive": 45,   # Flash drive
    "RAM": 35,
    "CPU": 180
}

# --------------------
# YOLO + Camera setup
# --------------------
model = YOLO("best.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 15)

frame_count = 0
last_label = None  # prevents servo jitter

print("E-Waste sorting started (CTRL+C to stop)")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Run YOLO every 3 frames
        if frame_count % 3 == 0:
            results = model.predict(
                frame,
                conf=0.25,
                imgsz=320,
                verbose=False
            )

            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes

                # Pick highest confidence detection
                best_i = int(boxes.conf.argmax().item())
                best_box = boxes[best_i]

                cls = int(best_box.cls[0])
                conf = float(best_box.conf[0])
                label = model.names[cls]

                print(f"Detected: {label} ({conf:.2f})")

                # Confidence threshold
                if conf < 0.5:
                    continue

                # Move servo only if new object detected
                if label in ANGLE_MAP and label != last_label:
                    angle = ANGLE_MAP[label]
                    print(f"→ Moving servo to {angle}° for {label}")
                    move_servo(angle)
                    last_label = label

except KeyboardInterrupt:
    print("\nStopping system...")

finally:
    cap.release()
    move_servo(0)   # reset servo on exit
    servo.detach()
