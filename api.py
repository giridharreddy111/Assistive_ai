from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2

from emotion.emotion_detector import EmotionDetector
from obstacle.obstacle_detector import ObstacleDetector


app = FastAPI()

# ADD THIS BLOCK
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

    emotion_result = emotion_system.process(img)
    obstacle_result = obstacle_system.process(img)

    return {
        "emotion": emotion_result,
        "obstacle": obstacle_result
    }