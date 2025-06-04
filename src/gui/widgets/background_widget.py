from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap.isNull():
            painter.drawPixmap(self.rect(), self.pixmap)
            painter.setOpacity(0.25)  # Ajuste l'opacité pour plus ou moins de lumière
            painter.fillRect(self.rect(), Qt.white)
            painter.setOpacity(1.0)
        super().paintEvent(event)