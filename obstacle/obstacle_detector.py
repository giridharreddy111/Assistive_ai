from ultralytics import YOLO
import cv2
import numpy as np

class ObstacleDetector:

    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def process(self, frame):

        results = self.model(frame, imgsz=320, verbose=False)

        h, w, _ = frame.shape
        center_x = w // 2

        for r in results:
            for box in r.boxes:

                confidence = float(box.conf[0])
                if confidence < 0.4:
                    continue

                x1, y1, x2, y2 = box.xyxy[0]
                area = (x2 - x1) * (y2 - y1)

                # ❗ ignore very small objects (far objects)
                if area < 50000:
                    continue

                # ❗ only consider objects in front
                obj_center = int((x1 + x2) / 2)
                if abs(obj_center - center_x) > w * 0.25:
                    continue

                # ❗ ONLY VERY CLOSE OBJECT → BEEP
                if area > 140000:
                    distance = 0   # very close ONLY
                    print("Very close obstacle detected")

                    return {
                        "object": "obstacle",
                        "distance": distance
                    }

        # -------- STRICT WALL DETECTION (VERY CLOSE ONLY) --------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)

        # VERY VERY STRICT → only when wall is extremely close
        if blur < 10 and brightness > 140:
            print("Very close wall detected")

            return {
                "object": "wall",
                "distance": 0
            }

        return None
