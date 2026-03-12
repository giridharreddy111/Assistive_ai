from ultralytics import YOLO

class ObstacleDetector:

    def __init__(self):

        # Load YOLO model
        self.model = YOLO("yolov8n.pt")

    def process(self, frame):

        results = self.model(frame, verbose=False)

        for r in results:

            for box in r.boxes:

                cls = int(box.cls[0])
                label = self.model.names[cls]

                # Ignore person because emotion detector handles it
                if label == "person":
                    continue

                confidence = float(box.conf[0])

                if confidence < 0.3:
                    continue

                print("Obstacle detected:", label)

                return {
                    "object": label
                }

        return None