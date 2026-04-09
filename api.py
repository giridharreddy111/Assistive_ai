import os
os.environ["OMP_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import numpy as np
import cv2
import time

from rapidocr_onnxruntime import RapidOCR
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
rapid_ocr = RapidOCR()

TEXT_MODE = False
LAST_TEXT = ""
LAST_TEXT_TIME = 0

# -----------------------------
def enhance_low_light(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced = cv2.merge([l_enhanced, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    return enhanced

# -----------------------------
def group_into_lines(result):
    items = []
    for item in result:
        text = item[1].strip()
        confidence = float(item[2])

        top_y = item[0][0][1]
        bot_y = item[0][3][1]
        left_x = item[0][0][0]
        height = abs(bot_y - top_y)
        center_y = (top_y + bot_y) / 2

        if confidence >= 0.5 and len(text) >= 2:
            items.append({
                "center_y": center_y,
                "left_x": left_x,
                "height": height,
                "text": text
            })

    if not items:
        return []

    heights = sorted([i["height"] for i in items])
    median_height = heights[len(heights)//2]
    threshold = median_height * 0.5

    items.sort(key=lambda x: x["center_y"])

    lines = []
    current_line = [items[0]]
    current_center_y = items[0]["center_y"]

    for item in items[1:]:
        if abs(item["center_y"] - current_center_y) <= threshold:
            current_line.append(item)
        else:
            lines.append(current_line)
            current_line = [item]

    lines.append(current_line)

    result_lines = []
    for line in lines:
        line.sort(key=lambda x: x["left_x"])
        line_text = " ".join([w["text"] for w in line])
        result_lines.append(line_text)

    return result_lines

# -----------------------------
def detect_text(frame):
    try:
        enhanced = enhance_low_light(frame)

        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        if np.mean(gray) < 127:
            enhanced = cv2.bitwise_not(enhanced)

        output = rapid_ocr(enhanced, use_cls=False)
        result = output[0] if isinstance(output, tuple) else output

        if not result:
            return []

        return group_into_lines(result)

    except:
        return []

# -----------------------------
@app.post("/toggle-text-mode")
def toggle_text_mode():
    global TEXT_MODE, LAST_TEXT, LAST_TEXT_TIME

    TEXT_MODE = not TEXT_MODE
    LAST_TEXT = ""
    LAST_TEXT_TIME = 0

    return {"mode": "text" if TEXT_MODE else "normal"}

# -----------------------------
@app.post("/detect")
async def detect(frame: UploadFile = File(...)):
    global TEXT_MODE, LAST_TEXT, LAST_TEXT_TIME

    contents = await frame.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if TEXT_MODE:
        if time.time() - LAST_TEXT_TIME < 2:
            return {"mode": "text", "text": ""}

        LAST_TEXT_TIME = time.time()
        lines = detect_text(img)

        if lines:
            full_text = ". ".join(lines)
            full_text = full_text.replace("|", " ")
            full_text = full_text.replace("  ", " ")

            if full_text != LAST_TEXT:
                LAST_TEXT = full_text
                return {"mode": "text", "text": full_text}
        else:
            LAST_TEXT = ""

        return {"mode": "text", "text": ""}

    emotion_result = emotion_system.process(img)
    if emotion_result:
        return {
            "mode": "normal",
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"],
            "obstacle": False,
            "distance": None,
            "text": ""
        }

    obstacle_result = obstacle_system.process(img)
    if obstacle_result:
        return {
            "mode": "normal",
            "emotion": None,
            "confidence": 0,
            "obstacle": True,
            "distance": obstacle_result["distance"],
            "text": ""
        }

    return {
        "mode": "normal",
        "emotion": None,
        "confidence": 0,
        "obstacle": False,
        "distance": None,
        "text": ""
    }

# -----------------------------
app.mount("/", StaticFiles(directory="web", html=True), name="web")
