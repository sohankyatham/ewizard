from ultralytics import YOLO
import cv2

if __name__ == '__main__':
    model = YOLO('best.pt')
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)
    
    frame_count = 0
    annotated = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Only run detection every 3 frames
        if frame_count % 3 == 0:
            results = model.predict(frame, conf=0.25, imgsz=320, verbose=False)
            annotated = results[0].plot()
            
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                print(f"Detected: {model.names[cls]} ({conf:.2f})")
        
        if annotated is not None:
            cv2.imshow('E-Waste Detector', annotated)
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()