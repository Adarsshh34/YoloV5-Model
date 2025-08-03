from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image
import io

app = FastAPI()

# Allow CORS (replace with your frontend origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pretrained YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# List of labels considered cheating
cheating_labels = ["book", "cell phone", "mobile phone","laptop"]

@app.post("/detect-cheating")
async def detect_cheating(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    results = model(image)
    detected = results.pandas().xyxy[0]["name"].tolist()

    # Count how many times "person" appears
    person_count = detected.count("person")
    
    # # Check for cheating objects
    # cheating_objects = [obj for obj in detected if obj in cheating_labels]

    # Detect cheating only if:
    # 1. More than 1 person is detected
    # 2. Any book or mobile phone is detected
    cheating_detected = person_count > 1 or any(label in cheating_labels for label in detected)
    
    return {
        "cheating_detected": cheating_detected,
        "detected_objects": detected
    }
