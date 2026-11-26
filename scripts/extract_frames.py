import cv2
import os

# ==========================
# AYARLAR
# ==========================

VIDEO_FOLDER = "/home/azat/teknofest_yolo/datasets2/drone/videos"
OUTPUT_FOLDER = "/home/azat/teknofest_yolo/datasets2/drone/images"

SAVE_EVERY = 0.08 # Her 0.10 saniyede 1 fotoğraf (≈10 FPS)

# ==========================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

counter = 0

videos = sorted(os.listdir(VIDEO_FOLDER))

for video in videos:

    if not video.lower().endswith(".mp4"):
        continue

    print(f"\nİşleniyor -> {video}")

    path = os.path.join(VIDEO_FOLDER, video)

    cap = cv2.VideoCapture(path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    frame_skip = max(1, int(fps * SAVE_EVERY))

    print(f"FPS: {fps:.1f}")
    print(f"Her {frame_skip}. kare kaydedilecek.")

    frame_id = 0
    saved = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_id += 1

        if frame_id % frame_skip != 0:
            continue

        filename = f"frame_{counter:06d}.jpg"

        cv2.imwrite(
            os.path.join(OUTPUT_FOLDER, filename),
            frame
        )

        counter += 1
        saved += 1

    cap.release()

    print(f"Kaydedilen frame : {saved}")

print("\n===============================")
print(f"TOPLAM KAYDEDİLEN FRAME : {counter}")
print("===============================")
