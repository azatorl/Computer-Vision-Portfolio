from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPoint, QTimer


class NamluGostergesi(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.azimut = 0.0

        # Radar sweep
        self.sweep_angle = -45.0
        self.sweep_direction = 1.0

        # Radar blipleri: (angle, radius_ratio, alpha)
        self.blips = []

        self.setMinimumSize(160, 160)

        # Yaklaşık 20 FPS radar animasyonu
        self.radar_timer = QTimer(self)
        self.radar_timer.timeout.connect(self.radar_animasyon)
        self.radar_timer.start(70)

    def veri_guncelle(self, azimut):
        self.azimut = azimut
        self.update()

    def radar_animasyon(self):

        # Sweep hareketi
        self.sweep_angle += 0.7 * self.sweep_direction

        if self.sweep_angle >= 45:
            self.sweep_angle = 45
            self.sweep_direction = -1.0

        elif self.sweep_angle <= -45:
            self.sweep_angle = -45
            self.sweep_direction = 1.0

        # Sweep geçerken birkaç radar noktası oluştur
        import random

        for _ in range(2):
            if random.random() < 0.18:
                angle = self.sweep_angle + random.uniform(-4, 4)
                radius_ratio = random.uniform(0.25, 0.95)
                self.blips.append(
                    [angle, radius_ratio, 255]
                )

        # Eski noktaları soldur
        yeni_blips = []

        for angle, radius_ratio, alpha in self.blips:
            alpha -= 3

            if alpha > 0:
                yeni_blips.append(
                    [angle, radius_ratio, alpha]
                )

        self.blips = yeni_blips[-20:]

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        r = min(w, h) / 2 - 10
        merkez = QPoint(
            int(w / 2),
            int(h / 2)
        )

        # =====================================================
        # RADAR HALKALARI
        # =====================================================

        painter.setPen(
            QPen(
                QColor(0, 180, 0),
                2
            )
        )

        painter.drawEllipse(
            merkez,
            int(r),
            int(r)
        )

        painter.setPen(
            QPen(
                QColor(0, 80, 0),
                1,
                Qt.DashLine
            )
        )

        for oran in (0.33, 0.66):
            painter.drawEllipse(
                merkez,
                int(r * oran),
                int(r * oran)
            )

        # =====================================================
        # YÖN İŞARETLERİ
        # =====================================================

        painter.setPen(
            QPen(
                QColor(0, 255, 0),
                1
            )
        )

        painter.setFont(
            QFont(
                "Consolas",
                9,
                QFont.Bold
            )
        )

        for angle in range(0, 360, 30):

            painter.save()

            painter.translate(merkez)
            painter.rotate(angle)

            line_len = 0.86 if angle % 90 == 0 else 0.91

            painter.drawLine(
                0,
                int(-r),
                0,
                int(-r * line_len)
            )

            painter.restore()

        # Kuzey / Güney / Doğu / Batı

        yonler = [
            ("K", 0),
            ("D", 90),
            ("G", 180),
            ("B", 270)
        ]

        for text, angle in yonler:

            painter.save()

            painter.translate(merkez)
            painter.rotate(angle)

            metrics = painter.fontMetrics()
            tw = metrics.horizontalAdvance(text)

            painter.drawText(
                int(-tw / 2),
                int(-r * 0.70),
                text
            )

            painter.restore()

        # =====================================================
        # RADAR BLIPLERI
        # =====================================================

        for angle, radius_ratio, alpha in self.blips:

            painter.save()

            painter.translate(merkez)
            painter.rotate(angle)

            x = 0
            y = int(-r * radius_ratio)

            painter.setPen(
                QPen(
                    QColor(
                        0,
                        255,
                        120,
                        int(alpha)
                    ),
                    2
                )
            )

            painter.setBrush(
                QColor(
                    0,
                    255,
                    120,
                    int(alpha)
                )
            )

            painter.drawEllipse(
                QPoint(x, y),
                4,
                4
            )

            painter.restore()

        # =====================================================
        # SWEEP ÇİZGİSİ
        # =====================================================

        painter.save()

        painter.translate(merkez)
        painter.rotate(self.sweep_angle)

        # Ana sweep
        painter.setPen(
            QPen(
                QColor(0, 255, 100, 210),
                2
            )
        )

        painter.drawLine(
            0,
            0,
            0,
            int(-r * 0.90)
        )

        # Sweep'in arkasında hafif iz
        painter.setPen(
            QPen(
                QColor(0, 255, 100, 50),
                4
            )
        )

        painter.drawLine(
            0,
            0,
            0,
            int(-r * 0.78)
        )

        painter.restore()

        # =====================================================
        # MERKEZ NOKTASI
        # =====================================================

        painter.setPen(
            QPen(
                QColor(0, 255, 0),
                1
            )
        )

        painter.setBrush(
            QColor(
                0,
                255,
                0
            )
        )

        painter.drawEllipse(
            merkez,
            4,
            4
        )

        # =====================================================
        # ALT AÇI
        # =====================================================

        painter.setFont(
            QFont(
                "Consolas",
                8,
                QFont.Bold
            )
        )

        angle_text = f"{self.azimut:.1f}°"

        metrics = painter.fontMetrics()
        tw = metrics.horizontalAdvance(angle_text)

        painter.drawText(
            int(w / 2 - tw / 2),
            int(h - 2),
            angle_text
        )

        painter.end()
