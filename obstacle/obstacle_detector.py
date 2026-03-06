from ultralytics import YOLO


class ObstacleDetector:

    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def process(self, frame):

        results = self.model(frame, verbose=False)

        h, w, _ = frame.shape
        center_min = int(w * 0.3)
        center_max = int(w * 0.7)

        detected_object = None
        proximity = None

        for r in results:
            for box in r.boxes:

                confidence = float(box.conf[0])
                if confidence < 0.5:
                    continue

                cls = int(box.cls[0])
                label = self.model.names[cls]

                # ignore person (since emotion system handles that)
                if label == "person":
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                box_center = (x1 + x2) // 2

                if center_min < box_center < center_max:

                    area = (x2 - x1) * (y2 - y1)

                    detected_object = label

                    if area > 80000:
                        proximity = "near"
                    elif area > 40000:
                        proximity = "medium"
                    else:
                        proximity = "far"

                    print(f"Obstacle: {detected_object} | Distance: {proximity}")

                    return {
                        "object": detected_object,
                        "distance": proximity
                    }

        return None