import cv2
from deepface import DeepFace


class EmotionDetector:

    def __init__(self):

        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def process(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        if len(faces) == 0:
            return None

        x, y, w, h = faces[0]

        face = frame[y:y+h, x:x+w]

        try:

            result = DeepFace.analyze(
                face,
                actions=["emotion"],
                enforce_detection=False
            )

            if isinstance(result, list):
                result = result[0]

            emotion = str(result["dominant_emotion"])
            confidence = float(result["emotion"][emotion])

            return {
                "emotion": emotion,
                "confidence": confidence
            }

        except:
            return None