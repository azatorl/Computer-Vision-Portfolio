from datetime import datetime
import random
import serial
import threading
import sys
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QFrame, QShortcut
from PyQt5.uic import loadUi

try:
    from joystick_thread import JoystickThread
    JOYSTICK_THREAD_VAR = True
except ImportError:
    JOYSTICK_THREAD_VAR = False

try:
    from yolo_detector import YOLOv8Thread
    YOLO_VAR = True
except ImportError:
    YOLO_VAR = False


class KomutaMerkezi(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mevcut_asama = 0
        self.e_stop_aktif = False
        self.namlu_gosterge = None
        self.son_hedef_kilitli = False

        loadUi("arayuz.ui", self)

        # Eski sağ panel pusulasını gizle
        if hasattr(self, "widget_gosterge"):
            self.widget_gosterge.show()

        # Kameranın üzerine pusula overlay
        self.namlu_gosterge = None
        try:
            from namlu_gostergesi import NamluGostergesi

            self.namlu_gosterge = NamluGostergesi(self.label_kamera)
            self.namlu_gosterge.setFixedSize(150, 150)

            def konumlandir_pusula():
                self.namlu_gosterge.move(
                    self.label_kamera.width() - 160,
                    10
                )

            self._konumlandir_pusula = konumlandir_pusula
            self.namlu_gosterge.raise_()
            self.namlu_gosterge.show()

        except Exception as e:
            print("KAMERA PUSULA OVERLAY HATASI:", e)

        self._last_status_text = ""

        # Canlı olay akışı için son hedef durumu
        self._last_log_target = None
        self._last_log_friend = None
        self._last_ai_info_text = ""

        # Mission Timer
        # Manuel menzil seçimi: sadece 5 / 10 / 15 m
        MENZIL_M = 5
        self.menzil_m = MENZIL_M

        if MENZIL_M not in (5, 10, 15):
            MENZIL_M = 5

        self.menzil_m = MENZIL_M

        if hasattr(self, "lcdNumber"):
            self.lcdNumber.display(self.menzil_m)

            # LCD üzerine küçük "m" birimi
            self.menzil_birim = QLabel(self.lcdNumber)
            self.menzil_birim.setText("m")
            self.menzil_birim.setAlignment(Qt.AlignCenter)
            self.menzil_birim.setStyleSheet(
                "QLabel {"
                "color: #00FF00;"
                "font-family: 'Consolas';"
                "font-size: 11px;"
                "font-weight: bold;"
                "background: transparent;"
                "}"
            )
            self.menzil_birim.setGeometry(
                self.lcdNumber.width() - 28,
                self.lcdNumber.height() - 24,
                20,
                18
            )
            self.menzil_birim.raise_()

        self.mission_seconds = 0
        self.mission_timer = QTimer(self)
        self.mission_timer.timeout.connect(self.mission_timer_guncelle)
        self.mission_timer.start(1000)

        # FPS / inference bilgi paneli: ana YOLO akışından bağımsız güncellenir
        self.performance_timer = QTimer(self)
        self.performance_timer.timeout.connect(self.performance_guncelle)
        self.performance_timer.start(500)

        self.mission_label = QLabel(self)
        self.mission_label.setGeometry(12, self.height() - 46, 205, 32)
        self.mission_label.setAlignment(Qt.AlignCenter)
        self.mission_label.setText("MISSION TIME: 00:00:00")
        self.mission_label.setStyleSheet(
            "QLabel {"
            "background-color: #020402;"
            "color: #00FF00;"
            "font-family: 'Consolas';"
            "font-size: 12px;"
            "font-weight: bold;"
            "border: 1px solid #00FF00;"
            "border-radius: 3px;"
            "padding: 3px;"
            "}"
        )

        # Pusula: yavaş tarama hareketi
        self.pusula_aci = 0.0
        self.pusula_yon = 1.0

        self.pusula_timer = QTimer(self)
        self.pusula_timer.timeout.connect(self.pusula_tarama)
        self.pusula_timer.start(80)

        # Sağ panel: Sistem durum göstergesi
        if hasattr(self, "widget_gosterge"):
            self.system_status = QLabel(self.widget_gosterge)
            self.system_status.setGeometry(8, 8, 310, 154)
            self.system_status.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.system_status.setText(
                "SYSTEM STATUS\n"
                "━━━━━━━━━━━━━━━━\n"
                "CAMERA    : ONLINE\n"
                "AI        : ONLINE\n"
                "TARGET    : --\n"
                "CONF      : --\n"
                "YOLO FPS  : --\n"
                "STATUS    : WAITING"
            )
            self.system_status.setStyleSheet(
                "QLabel {"
                "background-color: #020402;"
                "color: #00FF00;"
                "font-family: 'Consolas';"
                "font-size: 13px;"
                "font-weight: bold;"
                "border: 1px solid #00FF00;"
                "border-radius: 4px;"
                "padding: 6px;"
                "}"
            )

        # Manuel menzil kısayolları
        QShortcut("1", self, activated=lambda: self.menzil_degistir(5), context=Qt.ApplicationShortcut)
        QShortcut("2", self, activated=lambda: self.menzil_degistir(10), context=Qt.ApplicationShortcut)
        QShortcut("3", self, activated=lambda: self.menzil_degistir(15), context=Qt.ApplicationShortcut)

        self.butonlari_bagla()

        # Arduino Seri Port Dinleyici Thread Başlatma
        threading.Thread(target=self.arduino_dinle, daemon=True).start()

        if JOYSTICK_THREAD_VAR:
            self.joystick_thread = JoystickThread()
            self.joystick_thread.eksen_signal.connect(self.joystick_eksen_islem)
            self.joystick_thread.buton_signal.connect(self.joystick_buton_islem)
            self.joystick_thread.durum_signal.connect(self.joystick_durum_islem)
            self.joystick_thread.start()

        if YOLO_VAR:
            try:
                self.ai_thread = YOLOv8Thread()
                self.ai_thread.tespit_signal.connect(self.canli_tespit_islem)
                self.ai_thread.start()
            except Exception as e:
                print("AI Thread Başlatılamadı:", e)

        self.haber_akisi_ekle("SATÜRN Hava Savunma Sistemi Başlatıldı.", "SİSTEM")

    def performance_guncelle(self):
        if not hasattr(self, "system_status") or not hasattr(self, "ai_thread"):
            return

        fps = getattr(self.ai_thread, "yolo_fps", 0.0)
        infer = getattr(self.ai_thread, "inference_ms", 0.0)

        target = getattr(self, "_last_target_name", "--")
        conf = getattr(self, "_last_target_conf", "--")
        status = getattr(self, "_last_target_status", "WAITING")
        count = getattr(self.ai_thread, "target_count", 0)

        text = (
            "SYSTEM STATUS\n"
            "━━━━━━━━━━━━━━━━\n"
            "CAMERA    : ONLINE\n"
            "AI        : ONLINE\n"
            f"TARGET    : {target}\n"
            f"CONF      : {conf}\n"
            f"TARGETS   : {count}\n"
            f"YOLO FPS  : {fps:.1f}\n"
            f"INFER     : {infer:.1f} ms\n"
            f"STATUS    : {status}"
        )

        if text != self._last_status_text:
            self.system_status.setText(text)
            self._last_status_text = text

    def mission_timer_guncelle(self):
        self.mission_seconds += 1
        saat = self.mission_seconds // 3600
        dakika = (self.mission_seconds % 3600) // 60
        saniye = self.mission_seconds % 60

        if hasattr(self, "mission_label"):
            self.mission_label.setText(
                f"MISSION TIME: {saat:02d}:{dakika:02d}:{saniye:02d}"
            )

    def pusula_tarama(self):
        if not self.namlu_gosterge:
            return

        self.pusula_aci += 1.2 * self.pusula_yon

        if self.pusula_aci >= 45:
            self.pusula_aci = 45
            self.pusula_yon = -1.0

        elif self.pusula_aci <= -45:
            self.pusula_aci = -45
            self.pusula_yon = 1.0

        self.namlu_gosterge.veri_guncelle(self.pusula_aci)

    def arduino_dinle(self):
        """Arduino'dan Seri Port üzerinden gelen E-Stop verisini okur."""
        try:
            # Bilgisayarındaki Arduino COM portuna göre burayı düzenle (Örn: 'COM3', 'COM4')
            ser = serial.Serial('COM3', 9600, timeout=1) # COM3 yerine Arduino'nun portunu yaz
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line == "STOP" and not self.e_stop_aktif:
                    self.e_stop_aktif = True
                    self.haber_akisi_ekle("DIŞ ACİL DURDUR BUTONUNA BASILDI! Motorlar ve Lazer Kilitlendi.", "TEHLİKE")
                elif line == "OK" and self.e_stop_aktif:
                    self.e_stop_aktif = False
                    self.haber_akisi_ekle("Acil durdurma devreden çıkarıldı. Sistem hazır.", "BİLGİ")
        except Exception as e:
            print("Arduino bağlantı hatası (Port bulunamadı veya meşgul):", e)

    def haber_akisi_ekle(self, mesaj, tur="BİLGİ"):
        """Arayüzün sağındaki haber/log alanına zaman damgalı metin basar."""
        zaman = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{zaman}] [{tur}] {mesaj}"

        if hasattr(self, "txt_haber_akisi"):
            self.txt_haber_akisi.append(formatted_msg)
            self.txt_haber_akisi.verticalScrollBar().setValue(
                self.txt_haber_akisi.verticalScrollBar().maximum()
            )

    def butonlari_bagla(self):
        for i in range(1, 5):
            btn_g = f"btn_geri_{i}" if i > 1 else "btn_geri"
            btn_i = f"btn_ileri_{i}" if i > 1 else "btn_ileri"

            if hasattr(self, btn_g):
                getattr(self, btn_g).clicked.connect(self.onceki_asama)
            if hasattr(self, btn_i):
                getattr(self, btn_i).clicked.connect(self.sonraki_asama)

        btn_ates_elem = getattr(self, "btn_ates", getattr(self, "btn_ates_2", None))
        if btn_ates_elem and hasattr(btn_ates_elem, "clicked"):
            btn_ates_elem.clicked.connect(self.ates_et)

        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(lambda: self.haber_akisi_ekle("Mod: OTONOM Seçildi", "SİSTEM"))
        if hasattr(self, "pushButton_2"):
            self.pushButton_2.clicked.connect(lambda: self.haber_akisi_ekle("Mod: MANUEL Seçildi", "SİSTEM"))

    def sonraki_asama(self):
        self.mevcut_asama = (self.mevcut_asama + 1) % 3
        self.sayfa_guncelle()

    def onceki_asama(self):
        self.mevcut_asama = (self.mevcut_asama - 1) % 3
        self.sayfa_guncelle()

    def sayfa_guncelle(self):
        if hasattr(self, "stackedWidget"):
            self.stackedWidget.setCurrentIndex(self.mevcut_asama)
        self.haber_akisi_ekle(f"Görev Modu Değiştirildi: Aşama {self.mevcut_asama + 1}", "SİSTEM")

    def joystick_durum_islem(self, baglandi, cihaz_adi):
        if baglandi:
            self.haber_akisi_ekle(f"DONANIM BAĞLANDI: {cihaz_adi}", "BAŞARILI")

    def joystick_eksen_islem(self, yaw, pitch):
        yaw_aci = round(yaw * 45.0, 1)
        pitch_aci = round(-pitch * 30.0, 1)

        if hasattr(self, "label_5"):
            self.label_5.setText(f"YAW : {yaw_aci}°")
        if hasattr(self, "label_6"):
            self.label_6.setText(f"PITCH : {pitch_aci}°")

        if self.namlu_gosterge and hasattr(self.namlu_gosterge, "veri_guncelle"):
            self.namlu_gosterge.veri_guncelle(yaw_aci)

    def joystick_buton_islem(self, buton_id):
        if buton_id == 0:
            self.ates_et()
        elif buton_id == 1:
            self.dis_acil_durdur_tetikle()

    def dis_acil_durdur_tetikle(self):
        """Yazılımsal / Manuel acil durdurma tetiği."""
        self.e_stop_aktif = not self.e_stop_aktif
        if self.e_stop_aktif:
            self.haber_akisi_ekle("DIŞ ACİL DURDUR BUTONUNA BASILDI! Motorlar ve Lazer Kilitlendi.", "TEHLİKE")
        else:
            self.haber_akisi_ekle("Acil durdurma devreden çıkarıldı. Sistem hazır.", "BİLGİ")

    def ates_et(self):
        """Ateş serbest komutu kontrolü."""
        if self.e_stop_aktif:
            self.haber_akisi_ekle("ATIŞ ENGELLENDİ: ACİL DURDURMA AKTİF!", "TEHLİKE")
            return

        if self.mevcut_asama == 0:
            sonuclar = [
                "ATEŞLEME YAPILDI - HEDEF İMHA EDİLDİ",
                "ATEŞLEME YAPILDI - HEDEF ISKALANDI",
                "ATIŞ GERÇEKLEŞTİ - TEKRAR NİŞAN ALINIYOR"
            ]
            secilen_sonuc = random.choice(sonuclar)
            tur = "ATIŞ" if "İMHA" in secilen_sonuc else "UYARI"
            self.haber_akisi_ekle(secilen_sonuc, tur)
        else:
            if not self.son_hedef_kilitli:
                self.haber_akisi_ekle("ATIŞ İSTEDİ REDDEDİLDİ: HEDEFE KİLİTLENME SAĞLANAMADI", "UYARI")
            else:
                olasilik = random.random()
                if olasilik > 0.3:
                    self.haber_akisi_ekle("HEDEF KİLİTLENMESİ TAMAM - HEDEF İMHA EDİLDİ", "ATIŞ")
                else:
                    self.haber_akisi_ekle("ATEŞLEME YAPILDI - HEDEF TEMASI SAĞLANAMADI", "UYARI")

    def canli_tespit_islem(self, frame, hedef_tur, is_dost, guven_orani, menzil_m, bbox, all_targets):
        if frame is None or frame.size == 0:
            return

        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2

        # Son hedef bilgilerini sadece bellekte tut.
        if hedef_tur != "HEDEF YOK" and bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            self._last_target_name = hedef_tur
            self._last_target_conf = f"{guven_orani}%"
            self._last_target_status = "DETECTED"

            # Canlı olay akışı: sadece durum değiştiğinde logla.
            if self._last_log_target != hedef_tur:
                self.haber_akisi_ekle(
                    f"{hedef_tur} hedefi tespit edildi - Güven: {guven_orani}%",
                    "HEDEF"
                )
                self._last_log_target = hedef_tur

            friend_state = "DOST" if is_dost else "DÜŞMAN"

            if self._last_log_friend != friend_state:
                self.haber_akisi_ekle(
                    f"Hedef sınıflandırması: {friend_state}",
                    "TANI"
                )
                self._last_log_friend = friend_state

        else:
            self._last_target_name = "--"
            self._last_target_conf = "--"
            self._last_target_status = "NO TARGET"

            if self._last_log_target is not None:
                self.haber_akisi_ekle(
                    "Hedef kaybedildi.",
                    "HEDEF"
                )
                self._last_log_target = None
                self._last_log_friend = None

        if self.e_stop_aktif:
            self.son_hedef_kilitli = False
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 120), -1)
            cv2.putText(frame, "ACIL DURDURMA AKTIF", (cx - 210, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)
            cv2.putText(frame, "SISTEM KILITLENDI / ATIS ENGELLENDI", (cx - 240, cy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            x1, y1, x2, y2 = bbox

            if x2 > x1 and y2 > y1:
                hedef_merkez_x = (x1 + x2) // 2
                hedef_merkez_y = (y1 + y2) // 2

                fark_x = abs(cx - hedef_merkez_x)
                fark_y = abs(cy - hedef_merkez_y)

                self.son_hedef_kilitli = (fark_x < 60 and fark_y < 60)

                # ============================================================
                # MULTI-TARGET BOUNDING BOXLARI
                # Ana hedef = kilit durumuna göre beyaz/yeşil
                # Diğer hedefler = beyaz
                # ============================================================

                for target in all_targets:
                    tx1, ty1, tx2, ty2 = target["bbox"]
                    tname = target["class_name"]
                    tconf = target["confidence"]

                    # Ana hedef mi?
                    ana_hedef = (
                        tx1 == x1 and
                        ty1 == y1 and
                        tx2 == x2 and
                        ty2 == y2
                    )

                    if ana_hedef and self.son_hedef_kilitli:
                        box_color = (0, 255, 0)
                        box_thickness = 4
                    else:
                        box_color = (255, 255, 255)
                        box_thickness = 2

                    cv2.rectangle(
                        frame,
                        (tx1, ty1),
                        (tx2, ty2),
                        box_color,
                        box_thickness
                    )

                    target_label = f"{tname} {tconf}%"

                    cv2.putText(
                        frame,
                        target_label,
                        (tx1 + 3, max(18, ty1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        box_color,
                        1,
                        cv2.LINE_AA
                    )

                # Ana hedefin mevcut bbox'u için aşağıdaki label sistemi korunuyor.
                # ============================================================

                # Model etiketi + confidence
                label = f"{hedef_tur} {guven_orani}%"

                (tw, th), _ = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    1
                )

                label_y = max(y1, th + 6)

                cv2.putText(
                    frame,
                    label,
                    (x1 + 3, label_y - 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        kamera_label = getattr(self, "label_kamera", None)
        if kamera_label and kamera_label.width() > 10 and kamera_label.height() > 10:
            scaled_pixmap = pixmap.scaled(
                kamera_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            kamera_label.setPixmap(scaled_pixmap)

    def menzil_degistir(self, deger):
        if deger not in (5, 10, 15):
            return

        self.menzil_m = deger

        if hasattr(self, "lcdNumber"):
            self.lcdNumber.display(self.menzil_m)

        if hasattr(self, "txt_haber_akisi"):
            self.haber_akisi_ekle(
                f"Menzil manuel olarak {self.menzil_m} m seçildi.",
                "MENZİL"
            )

    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        if delta > 0:
            sirali = [5, 10, 15]
            idx = sirali.index(self.menzil_m)
            self.menzil_degistir(sirali[min(idx + 1, 2)])

        elif delta < 0:
            sirali = [5, 10, 15]
            idx = sirali.index(self.menzil_m)
            self.menzil_degistir(sirali[max(idx - 1, 0)])

        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_1:
            self.menzil_m = 5
        elif key == Qt.Key_2:
            self.menzil_m = 10
        elif key == Qt.Key_3:
            self.menzil_m = 15
        else:
            super().keyPressEvent(event)
            return

        if hasattr(self, "lcdNumber"):
            self.lcdNumber.display(self.menzil_m)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_konumlandir_pusula"):
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(0, self._konumlandir_pusula)

    def closeEvent(self, event):
        if hasattr(self, "joystick_thread"):
            self.joystick_thread.running = False
            self.joystick_thread.wait()
        if hasattr(self, "ai_thread"):
            self.ai_thread.running = False
            self.ai_thread.wait()
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ana_pencere = KomutaMerkezi()
        ana_pencere.showMaximized()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"KRİTİK HATA OLUŞTU: {e}")