# import cv2
# import mediapipe as mp
# import time
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
# from deepface import DeepFace
# from emotion.speech import speak


# class EmotionDetector:

#     def __init__(self):

#         self.last_emotion_time = 0
#         self.EMOTION_INTERVAL = 0.6

#         base_options = python.BaseOptions(
#             model_asset_path="models/face_landmarker.task"
#         )

#         options = vision.FaceLandmarkerOptions(
#             base_options=base_options,
#             running_mode=vision.RunningMode.IMAGE,
#             num_faces=1
#         )

#         self.landmarker = vision.FaceLandmarker.create_from_options(options)

#     def process(self, frame):

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         mp_image = mp.Image(
#             image_format=mp.ImageFormat.SRGB,
#             data=rgb_frame
#         )

#         result = self.landmarker.detect(mp_image)

#         # ---------- NO FACE ----------
#         if not result.face_landmarks:
#             return {
#                 "face_detected": False,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         h, w, _ = frame.shape
#         landmarks = result.face_landmarks[0]

#         xs = [lm.x for lm in landmarks]
#         ys = [lm.y for lm in landmarks]

#         x_min = int(min(xs) * w)
#         y_min = int(min(ys) * h)
#         x_max = int(max(xs) * w)
#         y_max = int(max(ys) * h)

#         face = frame[y_min:y_max, x_min:x_max]

#         if face.size == 0:
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         # -------- FULL FACE VALIDATION --------
#         face_width = (x_max - x_min)
#         face_height = (y_max - y_min)

#         face_area = face_width * face_height
#         frame_area = frame.shape[0] * frame.shape[1]

#         # ✅ 1. SIZE CHECK
#         if face_area < 0.1 * frame_area:
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         # ✅ 2. ASPECT RATIO CHECK (full face ~ square)
#         ratio = face_width / face_height

#         if ratio < 0.75 or ratio > 1.3:
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         # ✅ 3. CENTER CHECK
#         frame_center_x = frame.shape[1] // 2
#         face_center_x = (x_min + x_max) // 2

#         if abs(face_center_x - frame_center_x) > frame.shape[1] * 0.25:
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         # -------- COOLDOWN --------
#         current_time = time.time()

#         if current_time - self.last_emotion_time < self.EMOTION_INTERVAL:
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }

#         try:

#             analysis = DeepFace.analyze(
#                 face,
#                 actions=["emotion"],
#                 enforce_detection=True,
#                 detector_backend="skip"
#             )

#             if isinstance(analysis, list):
#                 analysis = analysis[0]

#             emotion = analysis["dominant_emotion"]
#             confidence = analysis["emotion"][emotion]

#             print(f"Emotion: {emotion} | Confidence: {confidence}")

#             # speak only if confident
#             if confidence > 60:
#                 speak(f"The person looks {emotion}")

#             self.last_emotion_time = current_time

#             return {
#                 "face_detected": True,
#                 "emotion": emotion,
#                 "confidence": float(confidence)
#             }

#         except Exception as e:
#             print("Emotion error:", e)
#             return {
#                 "face_detected": True,
#                 "emotion": None,
#                 "confidence": 0
#             }
# import cv2
# import mediapipe as mp
# import time
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
# from deepface import DeepFace

# # ---------------- CONFIG (TUNE ONLY THIS) ----------------

# DISTANCE_STRICTNESS = 100
# # ↓ Decrease (100) → allow FAR faces
# # ↑ Increase (160+) → only allow NEAR faces

# MIN_FACE_AREA_RATIO = 0.02  
# MAX_FACE_AREA_RATIO = 0.40  

# MIN_RATIO = 0.75  
# MAX_RATIO = 1.2  

# CENTER_TOLERANCE = 0.30  

# CONFIDENCE_THRESHOLD = 65  

# SAVE_DEBUG = False  

# # --------------------------------------------------------


# class EmotionDetector:

#     def __init__(self):

#         self.last_emotion_time = 0
#         self.EMOTION_INTERVAL = 0.6

#         base_options = python.BaseOptions(
#             model_asset_path="models/face_landmarker.task"
#         )

#         options = vision.FaceLandmarkerOptions(
#             base_options=base_options,
#             running_mode=vision.RunningMode.IMAGE,
#             num_faces=1
#         )

#         self.landmarker = vision.FaceLandmarker.create_from_options(options)

#     def process(self, frame):

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         mp_image = mp.Image(
#             image_format=mp.ImageFormat.SRGB,
#             data=rgb_frame
#         )

#         result = self.landmarker.detect(mp_image)

#         debug_frame = frame.copy()

#         if not result.face_landmarks:
#             print("❌ NO FACE")
#             return False, None, 0

#         h, w, _ = frame.shape
#         landmarks = result.face_landmarks[0]

#         xs = [lm.x for lm in landmarks]
#         ys = [lm.y for lm in landmarks]

#         x_min = int(min(xs) * w)
#         y_min = int(min(ys) * h)
#         x_max = int(max(xs) * w)
#         y_max = int(max(ys) * h)

#         # DRAW LANDMARKS
#         for lm in landmarks:
#             x = int(lm.x * w)
#             y = int(lm.y * h)
#             cv2.circle(debug_frame, (x, y), 1, (0, 255, 0), -1)

#         cv2.rectangle(debug_frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

#         face = frame[y_min:y_max, x_min:x_max]

#         if face.size == 0:
#             return False, None, 0

#         # -------- VALIDATION --------
#         face_width = (x_max - x_min)
#         face_height = (y_max - y_min)

#         face_area = face_width * face_height
#         frame_area = frame.shape[0] * frame.shape[1]

#         valid = True

#         # SIZE CHECK
#         if face_area < MIN_FACE_AREA_RATIO * frame_area:
#             print("❌ TOO FAR (AREA SMALL)")
#             valid = False

#         if face_area > MAX_FACE_AREA_RATIO * frame_area:
#             print("❌ TOO CLOSE (AREA LARGE)")
#             valid = False

#         # 🔥 SIMPLE DISTANCE CHECK
#         if face_width < DISTANCE_STRICTNESS:
#             print("❌ TOO FAR FROM CAMERA")
#             valid = False

#         # RATIO CHECK
#         ratio = face_width / face_height
#         if ratio < MIN_RATIO or ratio > MAX_RATIO:
#             print("❌ BAD FACE RATIO:", ratio)
#             valid = False

#         # CENTER CHECK
#         frame_center_x = frame.shape[1] // 2
#         face_center_x = (x_min + x_max) // 2

#         if abs(face_center_x - frame_center_x) > frame.shape[1] * CENTER_TOLERANCE:
#             print("❌ FACE NOT CENTERED")
#             valid = False

#         # -------- FULL FACE CHECK --------
#         LEFT_EYE = [33, 133]
#         RIGHT_EYE = [362, 263]
#         NOSE = [1]
#         MOUTH = [13, 14]
#         LEFT_EAR = [234]
#         RIGHT_EAR = [454]

#         def is_visible(idx_list):
#             for idx in idx_list:
#                 lm = landmarks[idx]
#                 if lm.x < 0 or lm.x > 1 or lm.y < 0 or lm.y > 1:
#                     return False
#             return True

#         full_face = (
#             is_visible(LEFT_EYE) and
#             is_visible(RIGHT_EYE) and
#             is_visible(NOSE) and
#             is_visible(MOUTH) and
#             is_visible(LEFT_EAR) and
#             is_visible(RIGHT_EAR)
#         )

#         if not full_face:
#             print("❌ FULL FACE NOT VISIBLE")
#             valid = False

#         emotion = None
#         confidence = 0

#         if valid:
#             try:
#                 analysis = DeepFace.analyze(
#                     face,
#                     actions=["emotion"],
#                     enforce_detection=True,
#                     detector_backend="skip"
#                 )

#                 if isinstance(analysis, list):
#                     analysis = analysis[0]

#                 emotion = analysis["dominant_emotion"]
#                 confidence = analysis["emotion"][emotion]

#             except Exception as e:
#                 print("Emotion error:", e)

#         # -------- PRINT RESULT --------
#         status = "VALID" if valid else "INVALID"
#         print(f"{status} | Emotion: {emotion} | Confidence: {confidence:.2f}")

#         # SAVE DEBUG IMAGE
#         if SAVE_DEBUG:
#             filename = f"debug_{status}.jpg"
#             cv2.imwrite(filename, debug_frame)

#         return valid, emotion, confidence


# # ---------------- RUN CAMERA ----------------
# if __name__ == "__main__":

#     cap = cv2.VideoCapture(0)
#     detector = EmotionDetector()

#     print("Press 'q' to quit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         detector.process(frame)

#         cv2.imshow("Camera", frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from deepface import DeepFace
from emotion.speech import speak


class EmotionDetector:

    def __init__(self):

        self.last_emotion_time = 0
        self.EMOTION_INTERVAL = 0.8  # faster detection

        base_options = python.BaseOptions(
            model_asset_path="models/face_landmarker.task"
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1
        )

        self.landmarker = vision.FaceLandmarker.create_from_options(options)

    def process(self, frame):

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.landmarker.detect(mp_image)

        # ---------- NO FACE ----------
        if not result.face_landmarks:
            return None

        h, w, _ = frame.shape
        landmarks = result.face_landmarks[0]

        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]

        x_min = int(min(xs) * w)
        y_min = int(min(ys) * h)
        x_max = int(max(xs) * w)
        y_max = int(max(ys) * h)

        face = frame[y_min:y_max, x_min:x_max]

        if face.size == 0:
            return None

        current_time = time.time()

        # ---------- COOLDOWN ----------
        if current_time - self.last_emotion_time < self.EMOTION_INTERVAL:
            return {
                "emotion": None,
                "confidence": 0
            }

        try:

            analysis = DeepFace.analyze(
                face,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="skip"
            )

            if isinstance(analysis, list):
                analysis = analysis[0]

            emotion = analysis["dominant_emotion"]
            confidence = analysis["emotion"][emotion]

            print(f"Emotion: {emotion} | Confidence: {confidence}")

            if confidence > 55:
                speak(f"The person looks {emotion}")

            self.last_emotion_time = current_time

            return {
                "emotion": emotion,
                "confidence": float(confidence)
            }

        except Exception as e:
            print("Emotion error:", e)
            return None
