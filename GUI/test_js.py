import pygame
from PyQt5.QtCore import QThread, pyqtSignal


class JoystickThread(QThread):
    eksen_signal = pyqtSignal(float, float)
    buton_signal = pyqtSignal(int)
    durum_signal = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.joystick = None

    def run(self):
        pygame.init()
        pygame.joystick.init()

        while self.running:
            # Joystick Bağlantı Kontrolü
            if self.joystick is None:
                if pygame.joystick.get_count() > 0:
                    try:
                        self.joystick = pygame.joystick.Joystick(0)
                        self.joystick.init()
                        self.durum_signal.emit(True, self.joystick.get_name())
                    except Exception:
                       self.joystick = None
                 else:
                    self.durum_signal.emit(False, "Joystick Bulunamadı")
                    self.msleep(1000)
                    continue

            # Event Kuyruğunu Temizle ve Butonları Oku
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.buton_signal.emit(event.button)

            try:
                num_axes = self.joystick.get_numaxes()

                # Flight Simulator için aktif çalışan eksenler (0: Sağa/Sola, 1: İleri/Geri)
                raw_yaw = self.joystick.get_axis(0) if num_axes > 0 else 0.0
                raw_pitch = self.joystick.get_axis(1) if num_axes > 1 else 0.0

                # Ölü Bölge (Deadzone) Filtresi - Titremeleri engeller
                yaw = 0.0 if abs(raw_yaw) < 0.08 else raw_yaw
                pitch = 0.0 if abs(raw_pitch) < 0.08 else raw_pitch

                # Sinyali Arayüze Gönder
                self.eksen_signal.emit(float(yaw), float(pitch))

            except Exception as e:
                self.joystick = None
                self.durum_signal.emit(False, f"Bağlantı Hatası: {e}")

            # 30 Hz Yenileme Hızı
            self.msleep(33)

        pygame.quit()