import time
import pygame
from PyQt5.QtCore import QThread, pyqtSignal


class JoystickThread(QThread):
    # Eksen hareketleri: (yaw_ekseni, pitch_ekseni)
    eksen_signal = pyqtSignal(float, float)
    # Buton basışları: (button_id)
    buton_signal = pyqtSignal(int)
    # Bağlantı durumu: (baglandi_mi, cihaz_adi)
    durum_signal = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.joystick = None

    # joystick_thread.py içinde:
def run(self):
    pygame.init()
    pygame.joystick.init()

    while self.running:
        if self.joystick is None:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.durum_signal.emit(True, self.joystick.get_name())
            else:
                self.durum_signal.emit(False, "Joystick Bulunamadı")
                self.msleep(1000)
                continue

        # Event kuyruğunu temizle (Sistem kilitlenmesini ve kapanmayı önler)
        for event in pygame.event.get():
            pass

        try:
            yaw = round(self.joystick.get_axis(0), 2)
            pitch = round(self.joystick.get_axis(1), 2)

            if abs(yaw) < 0.1:
                yaw = 0.0
            if abs(pitch) < 0.1:
                pitch = 0.0

            self.eksen_signal.emit(yaw, pitch)

            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    self.buton_signal.emit(i)

        except Exception as e:
            self.joystick = None
            self.durum_signal.emit(False, f"Bağlantı Hatası: {e}")

        self.msleep(33)