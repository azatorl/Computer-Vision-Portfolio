import cv2
import time
from ultralytics import YOLO

# ==========================================================
# AYARLAR
# ==========================================================

MODEL_PATH = "../models/best.pt"
STREAM_URL = "tcp://10.42.0.61:8888"

CONFIDENCE = 0.40
IMG_SIZE = 640

# ==========================================================
# MODEL
# ==========================================================

print("=" * 50)
print("Teknofest Vision System")
print("=" * 50)

print("[INFO] Model yükleniyor...")

model = YOLO(MODEL_PATH)
model.to("cuda")

print("[OK] Model yüklendi.")
print("[OK] GPU : CUDA")
print("=" * 50)

# ==========================================================
# KAMERA
# ==========================================================

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("[ERROR] Kamera açılamadı!")
    exit()

print("[OK] Kamera bağlantısı başarılı.")

# ==========================================================
# FPS
# ==========================================================

prev_time = time.time()

# ==========================================================
# ANA DÖNGÜ
# ==========================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("[ERROR] Frame alınamadı.")
        break

    start = time.time()

    # ------------------------------------------------------
    # YOLO
    # ------------------------------------------------------

    results = model.predict(
        frame,
        imgsz=IMG_SIZE,
        conf=CONFIDENCE,
        device="cuda",
        verbose=False
    )

    inference = (time.time() - start) * 1000

    result = results[0]

    annotated = results[0].plot()

    boxes = result.boxes

    object_count = len(boxes)

    # ------------------------------------------------------
    # TESPİTLER
    # ------------------------------------------------------

    for idx, box in enumerate(boxes):

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cls = int(box.cls[0])

        conf = float(box.conf[0])

        class_name = model.names[cls]

        # Merkez noktası

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # Bounding Box

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # Merkez

        cv2.circle(
            annotated,
            (cx, cy),
            5,
            (0, 0, 255),
            -1
        )

        # ID

        cv2.putText(
            annotated,
            f"ID : {idx+1}",
            (x1, y1 - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

        # Sınıf

        cv2.putText(
            annotated,
            class_name,
            (x1, y1 - 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Confidence

        cv2.putText(
            annotated,
            f"{conf*100:.1f} %",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        # Merkez koordinatı

        cv2.putText(
            annotated,
            f"({cx},{cy})",
            (cx + 10, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2
        )

    # ------------------------------------------------------
    # FPS
    # ------------------------------------------------------

    current = time.time()

    fps = 1 / (current - prev_time)

    prev_time = current

    # ------------------------------------------------------
    # Bilgi Paneli
    # ------------------------------------------------------

    cv2.putText(
        annotated,
        f"FPS : {fps:.1f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        annotated,
        f"Inference : {inference:.1f} ms",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated,
        f"Objects : {object_count}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        annotated,
        "GPU : RTX 4070",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # ------------------------------------------------------
    # GÖSTER
    # ------------------------------------------------------

    cv2.imshow("Teknofest Vision v1.1", annotated)

    key = cv2.waitKey(1)

    if key == 27:
        break

# ==========================================================

cap.release()

cv2.destroyAllWindows()
