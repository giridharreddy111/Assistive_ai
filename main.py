import cv2
from emotion.emotion_detector import EmotionDetector
from obstacle.obstacle_detector import ObstacleDetector

def main():
    cap = cv2.VideoCapture(0)

    emotion_system = EmotionDetector()
    obstacle_system = ObstacleDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        emotion_system.process(frame)
        obstacle_system.process(frame)

        cv2.imshow("Assistive AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()