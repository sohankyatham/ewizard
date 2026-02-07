E-Waste Component Detection
A YOLOv8-based object detection model for identifying and classifying electronic waste components. Built for an automated e-waste sorting system.
Classes
IDComponent0CPU1RAM2USB_Drive39V_Battery
Requirements

Python 3.11
NVIDIA GPU with CUDA support (recommended)

Installation
bashpip install ultralytics opencv-python
Dataset Setup


Training
bashpy -3.11 train.py
Training parameters:

Model: YOLOv8n (nano)
Epochs: 100
Image size: 640x640
Batch size: 8

Live Demo
Run real-time detection using your webcam:
bashpy -3.11 live_demo.py
Press q to quit.

Files
FileDescriptiontrain.pyModel training scriptlive_demo.pyWebcam inference demodataset_train.pyDataset preparation and train/val splitewaste.yamlDataset configuration
Model Weights
After training, weights are saved to:

runs/train/weights/best.pt - Best performing model
runs/train/weights/last.pt - Final epoch model

