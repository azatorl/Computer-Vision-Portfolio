import subprocess
import cv2
import time
import numpy as np
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal


def renk_siniflandir(frame, bbox):
    """
    YOLO bbox içindeki baskın rengi Hue + Saturation ile belirler.

    MAVİ -> DOST
    KIRMIZI -> DUSMAN
    Belirsiz -> BILINMIYOR
    """

    x1, y1, x2, y2 = map(int, bbox)

    h_img, w_img = frame.shape[:2]

    x1 = max(0, min(x1, w_img - 1))
    x2 = max(0, min(x2, w_img))
    y1 = max(0, min(y1, h_img - 1))
    y2 = max(0, min(y2, h_img))

    if x2 <= x1 or y2 <= y1:
        return "BILINMIYOR"

    roi = frame[y1:y2, x1:x2]

    if roi.size == 0:
        return "BILINMIYOR"

    # Arka plan etkisini azaltmak için merkez bölge
    rh, rw = roi.shape[:2]

    margin_x = int(rw * 0.15)
    margin_y = int(rh * 0.15)

    if rw > 20 and rh > 20:
        roi = roi[
            margin_y:rh - margin_y,
            margin_x:rw - margin_x
        ]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    H = hsv[:, :, 0]
    S = hsv[:, :, 1]
    V = hsv[:, :, 2]

    # Düşük doygunluk ve çok karanlık pikselleri çıkar
    valid = (
        (S >= 80) &
        (V >= 60)
    )

    total_valid = int(np.count_nonzero(valid))

    if total_valid < 20:
        return "BILINMIYOR"

    hue_values = H[valid]

    # KIRMIZI: Hue 0-10 veya 170-179
    red_pixels = np.count_nonzero(
        (hue_values <= 10) |
        (hue_values >= 170)
    )

    # MAVİ: Hue 90-135
    blue_pixels = np.count_nonzero(
        (hue_values >= 90) &
        (hue_values <= 135)
    )

    red_ratio = red_pixels / total_valid
    blue_ratio = blue_pixels / total_valid

    threshold = 0.15

    if red_ratio >= threshold and red_ratio > blue_ratio:
        return "DUSMAN"

    if blue_ratio >= threshold and blue_ratio > red_ratio:
        return "DOST"

    return "BILINMIYOR"


class YOLOv8Thread(QThread):

    tespit_signal = pyqtSignal(object, str, bool, int, float, list, list)

    MODEL_PATH = "/home/azat/teknofest_yolo/runs/merged/rocket_airdefense_v2/weights/best.pt"

    TCP_URL = "tcp://10.42.0.61:8888"

    WIDTH = 1280
    HEIGHT = 720
    CONF = 0.25

    def __init__(self):
        super().__init__()

        self.running = True
        self.model = YOLO(self.MODEL_PATH)
        self.model.to("cuda")
        self.process = None
        self.yolo_fps = 0.0
        self.inference_ms = 0.0

    def run(self):

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "warning",
            "-f", "h264",
            "-i", self.TCP_URL,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", "1280x720",
            "-an",
            "-"
        ]

        try:

            print(">>> FFmpeg baslatiliyor...")
            print(">>> Kamera:", self.TCP_URL)

            self.process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=None,
                bufsize=10**8
            )

            frame_size = self.WIDTH * self.HEIGHT * 3

            frame_count = 0
            fps_start = time.perf_counter()

            print(">>> Frame bekleniyor...")

            while self.running:

                raw = self.process.stdout.read(frame_size)

                if len(raw) != frame_size:
                    print(f">>> Eksik frame: {len(raw)}/{frame_size}")
                    self.msleep(10)
                    continue

                frame = np.frombuffer(
                    raw,
                    dtype=np.uint8
                ).reshape(
                    self.HEIGHT,
                    self.WIDTH,
                    3
                ).copy()

                inference_start = time.perf_counter()

                # 1280x720 görüntüyü koru, AI için 640x360 kopya kullan
                ai_frame = cv2.resize(
                    frame,
                    (640, 360),
                    interpolation=cv2.INTER_AREA
                )

                results = self.model.track(
                    source=ai_frame,
                    imgsz=320,
                    conf=self.CONF,
                    half=True,
                    tracker="bytetrack.yaml",
                    persist=True,
                    verbose=False
                )

                self.inference_ms = (time.perf_counter() - inference_start) * 1000

                result = results[0]

                # FPS sayac
                frame_count += 1

                if frame_count % 30 == 0:
                    now = time.perf_counter()
                    elapsed = now - fps_start

                    if elapsed > 0:
                        self.yolo_fps = 30.0 / elapsed

                    fps_start = now

                    print(f">>> YOLO FPS: {self.yolo_fps:.1f}")

                if result.boxes is None or len(result.boxes) == 0:
                    self.target_count = 0
                    self.tespit_signal.emit(
                        frame,
                        "HEDEF YOK",
                        False,
                        0,
                        0.0,
                        [0, 0, 0, 0],
                        []
                    )
                    continue

                self.target_count = len(result.boxes)

                # Tüm detection'ları GUI'ye hazırla
                all_targets = []

                for i in range(len(result.boxes)):
                    box_i = result.boxes[i]

                    conf_i = float(box_i.conf.item())
                    cls_i = int(box_i.cls.item())
                    name_i = result.names[cls_i]

                    ax1, ay1, ax2, ay2 = map(
                        int,
                        box_i.xyxy[0].tolist()
                    )

                    # AI 640x360 -> kamera 1280x720
                    x1_i = int(ax1 * 2.0)
                    y1_i = int(ay1 * 2.0)
                    x2_i = int(ax2 * 2.0)
                    y2_i = int(ay2 * 2.0)

                    bbox_i = [x1_i, y1_i, x2_i, y2_i]

                    renk_i = renk_siniflandir(
                        frame,
                        bbox_i
                    )

                    # ByteTrack ID
                    if box_i.id is not None:
                        track_id_i = int(box_i.id.item())
                    else:
                        track_id_i = -1

                    # Hedef merkezi
                    center_x_i = (x1_i + x2_i) // 2
                    center_y_i = (y1_i + y2_i) // 2

                    all_targets.append({
                        "track_id": track_id_i,
                        "class_name": name_i,
                        "confidence": int(conf_i * 100),
                        "bbox": bbox_i,
                        "center": [center_x_i, center_y_i],
                        "friend": renk_i == "DOST"
                    })

                # En yüksek confidence'lı hedef = ana hedef
                best_index = int(
                    result.boxes.conf.argmax().item()
                )

                best_box = result.boxes[best_index]

                confidence = float(
                    best_box.conf.item()
                )

                class_id = int(
                    best_box.cls.item()
                )

                hedef_tur = result.names[class_id]

                ax1, ay1, ax2, ay2 = map(
                    int,
                    best_box.xyxy[0].tolist()
                )

                # AI 640x360 -> kamera 1280x720
                x1 = int(ax1 * 2.0)
                y1 = int(ay1 * 2.0)
                x2 = int(ax2 * 2.0)
                y2 = int(ay2 * 2.0)

                bbox = [x1, y1, x2, y2]

                guven_orani = int(
                    confidence * 100
                )

                renk_durumu = renk_siniflandir(
                    frame,
                    bbox
                )

                is_dost = (renk_durumu == "DOST")
                menzil_m = 0.0

                self.tespit_signal.emit(
                    frame,
                    hedef_tur,
                    is_dost,
                    guven_orani,
                    menzil_m,
                    bbox,
                    all_targets
                )

        except Exception as e:
            print()
            print("================================")
            print("YOLO THREAD HATASI")
            print("================================")
            print(e)
            print("================================")
            print()

        finally:
            if self.process is not None:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def stop(self):
        self.running = False
        if self.process is not None:
            try:
                self.process.kill()
            except Exception:
                pass
