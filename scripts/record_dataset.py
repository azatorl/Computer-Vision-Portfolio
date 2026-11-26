
import cv2
import time
from datetime import datetime

STREAM = "tcp://10.42.0.61:8888"

cap = cv2.VideoCapture(STREAM)

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

print("ENTER = Kayıt Başlat")
print("ESC = Çık")

while True:

    ret, frame = cap.read()

    if not ret:
        continue

    cv2.putText(frame, "ENTER = RECORD", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    cv2.imshow("Dataset Recorder", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 13:

        print("10 saniye sonra kayıt başlayacak...")

        for i in range(10,0,-1):

            ret, frame = cap.read()

            cv2.putText(frame, str(i),
                        (580,360),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        5,
                        (0,0,255),
                        8)

            cv2.imshow("Dataset Recorder", frame)

            cv2.waitKey(1000)

        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(
            filename,
            fourcc,
            60,
            (1280,720)
        )

        print("Kayıt başladı...")

        start = time.time()

        while time.time() - start < 40:

            ret, frame = cap.read()

            if not ret:
                continue

            out.write(frame)

            cv2.putText(frame,"REC",
                        (20,40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,0,255),
                        2)

            cv2.imshow("Dataset Recorder", frame)

            cv2.waitKey(1)

        out.release()

        print("Video kaydedildi:", filename)

    elif key == 27:

        break

cap.release()

cv2.destroyAllWindows()
