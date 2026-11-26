import subprocess
import cv2
import numpy as np
from ultralytics import YOLO

MODEL_PATH = "/home/azat/teknofest_yolo/runs/detect/rocket_baloon-2/weights/best.pt"
TCP_URL = "tcp://10.42.0.61:8888"


CONF = 0.25
WIDTH = 640
HEIGHT = 480

model = YOLO(MODEL_PATH)

ffmpeg_cmd = [
    "ffmpeg",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-i", TCP_URL,
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-"
]

pipe = subprocess.Popen(
    ffmpeg_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    bufsize=10**8
)

FRAME_SIZE = WIDTH * HEIGHT * 3

cv2.namedWindow("Teknofest YOLO", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Teknofest YOLO", 1280, 720)

while True:

    raw = pipe.stdout.read(FRAME_SIZE)

    if len(raw) != FRAME_SIZE:
        continue

    frame = np.frombuffer(raw, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))

    results = model.predict(
        frame,
        imgsz=640,
        conf=CONF,
        device=0,
        verbose=False
    )

    annotated = results[0].plot()

    cv2.imshow("Teknofest YOLO", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

pipe.kill()
cv2.destroyAllWindows()
