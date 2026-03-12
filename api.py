from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2

from emotion.emotion_detector import EmotionDetector
from obstacle.obstacle_detector import ObstacleDetector


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_system = EmotionDetector()
obstacle_system = ObstacleDetector()


@app.post("/detect")
async def detect(frame: UploadFile = File(...)):

    contents = await frame.read()

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # -------- EMOTION FIRST --------
    emotion_result = emotion_system.process(img)

    if emotion_result:

        return {
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"],
            "obstacle": False
        }

    # -------- NO FACE -> CHECK OBSTACLE --------
    obstacle_result = obstacle_system.process(img)

    if obstacle_result:

        return {
            "emotion": "no_face",
            "confidence": 0,
            "obstacle": True,
            "object": obstacle_result["object"]
        }

    # -------- NOTHING DETECTED --------
    return {
        "emotion": "no_face",
        "confidence": 0,
        "obstacle": False
    }


app.mount("/", StaticFiles(directory="web", html=True), name="web")