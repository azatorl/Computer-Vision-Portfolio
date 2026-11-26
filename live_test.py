import cv2
import time
from ultralytics import YOLO

MODEL_PATH = "/home/azat/teknofest_yolo/runs/detect/rocket_baloon-2/weights/best.pt"
STREAM = "tcp://10.42.0.61:8888"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(STREAM)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Kamera acilamadi!")
    exit()

prev = time.time()

while True:

    # Buffer'daki eski kareleri at
    for _ in range(5):
        cap.grab()

    ret, frame = cap.read()

    if not ret:
        continue

    results = model.predict(
        frame,
        imgsz=640,
        conf=0.5,
        verbose=False
    )

    frame = results[0].plot()

    now = time.time()
    fps = 1 / (now - prev)
    prev = now

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("YOLO Live", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
