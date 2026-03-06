import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from deepface import DeepFace


class EmotionDetector:

    def __init__(self):

        # Load MediaPipe Face Landmarker
        base_options = python.BaseOptions(
            model_asset_path="models/face_landmarker (1).task"
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1
        )

        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def process(self, frame):

        frame_height, frame_width, _ = frame.shape

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect face
        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks:
            print("No face detected")
            return None

        landmarks = result.face_landmarks[0]

        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]

        x_min = int(min(xs) * frame_width)
        y_min = int(min(ys) * frame_height)
        x_max = int(max(xs) * frame_width)
        y_max = int(max(ys) * frame_height)

        face_crop = frame[y_min:y_max, x_min:x_max]

        if face_crop.size == 0:
            return None

        face_crop = cv2.resize(face_crop, (224, 224))

        try:

            analysis = DeepFace.analyze(
                face_crop,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="skip"
            )

            if isinstance(analysis, list):
                analysis = analysis[0]

            emotion = analysis["dominant_emotion"]
            confidence = analysis["emotion"][emotion]

            print(f"Detected Emotion: {emotion} | Confidence: {round(confidence,2)}")

            # return emotion only if confidence good
            if confidence > 50:
                return emotion
            else:
                return None

        except Exception as e:
            print("Emotion error:", e)
            return None