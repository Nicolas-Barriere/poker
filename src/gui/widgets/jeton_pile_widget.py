from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter, QDrag
from PyQt5.QtCore import Qt, QMimeData, QSize, QPoint

class JetonPileWidget(QWidget):
    def __init__(self, couleur, count, img_path, joueur_idx=None, parent=None):
        super().__init__(parent)
        self.couleur = couleur  # ex: 'noir', 'rouge', ...
        self.count = count
        self.img_path = img_path
        self.joueur_idx = joueur_idx  # index du joueur propriétaire de la pile
        self.setFixedWidth(56)
        self.setAcceptDrops(False)
        self.setMouseTracking(True)
        self.drag_start_pos = None
        self.drag_count = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        pix = QPixmap(self.img_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        jeton_height = 48
        recouvrement = 40
        pile_height = jeton_height + (self.count - 1) * (jeton_height - recouvrement) if self.count > 0 else 0
        base_y = self.height() - pile_height
        for i in range(self.count):
            y = base_y + i * (jeton_height - recouvrement)
            painter.drawPixmap(4, y, pix)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drag_start_pos and (event.buttons() & Qt.LeftButton):
            jeton_height = 48
            recouvrement = 40
            pile_height = jeton_height + (self.count - 1) * (jeton_height - recouvrement) if self.count > 0 else 0
            base_y = self.height() - pile_height
            y = event.pos().y()
            if y < base_y:
                jetons_a_prendre = 1
            else:
                rel_y = y - base_y
                jetons_a_prendre = min(self.count, 1 + int(rel_y // (jeton_height - recouvrement)))
            if jetons_a_prendre > 0:
                mime = QMimeData()
                mime.setData('application/x-jeton', f"{self.couleur}:{jetons_a_prendre}:{self.joueur_idx}".encode())
                drag = QDrag(self)
                drag.setMimeData(mime)

                # Crée le pixmap de la pile
                pix = QPixmap(self.img_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pile_pix = QPixmap(56, 48 + (jetons_a_prendre - 1) * 8)
                pile_pix.fill(Qt.transparent)
                painter = QPainter(pile_pix)
                for i in range(jetons_a_prendre):
                    painter.drawPixmap(4, pile_pix.height() - 48 - (i * 8), pix)
                painter.end()
                drag.setPixmap(pile_pix)

                # Hotspot X (horizontal)
                delta_x = (self.width() - pile_pix.width()) // 2
                hotspot_x = event.pos().x() - delta_x

                # Hotspot Y (vertical)
                clicked_relative_y = y - base_y
                rel_index = min(jetons_a_prendre - 1, int(clicked_relative_y // (jeton_height - recouvrement)))
                hotspot_y = pile_pix.height() - (jetons_a_prendre - rel_index) * 8 + (clicked_relative_y % (jeton_height - recouvrement))

                drag.setHotSpot(QPoint(0, 0))
                drag.exec_(Qt.MoveAction)
            self.drag_start_pos = None


    def sizeHint(self):
        jeton_height = 48
        recouvrement = 32
        pile_height = jeton_height + (self.count - 1) * (jeton_height - recouvrement) if self.count > 0 else jeton_height
        return QSize(56, pile_height)

    def setCount(self, count):
        self.count = count
        jeton_height = 48
        recouvrement = 32
        pile_height = jeton_height + (self.count - 1) * (jeton_height - recouvrement) if self.count > 0 else jeton_height
        self.setMinimumHeight(pile_height)
        self.update()

    def resizeEvent(self, event):
        jeton_height = 48
        recouvrement = 32
        pile_height = jeton_height + (self.count - 1) * (jeton_height - recouvrement) if self.count > 0 else jeton_height
        self.setMinimumHeight(pile_height)
        super().resizeEvent(event)
