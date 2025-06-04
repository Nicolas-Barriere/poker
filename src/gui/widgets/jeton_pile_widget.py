from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter, QDrag
from PyQt5.QtCore import Qt, QMimeData, QSize

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
            # Correction : plus on clique bas, plus on prend de jetons
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
                # Pixmap pour le drag : une pile de jetons
                pix = QPixmap(self.img_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pile_pix = QPixmap(56, 48 + (jetons_a_prendre-1)*8)
                pile_pix.fill(Qt.transparent)
                painter = QPainter(pile_pix)
                for i in range(jetons_a_prendre):
                    painter.drawPixmap(4, pile_pix.height()-48-(i*8), pix)
                painter.end()
                drag.setPixmap(pile_pix)
                drag.setHotSpot(event.pos())
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
