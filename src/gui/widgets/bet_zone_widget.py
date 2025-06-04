from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QDrag
from PyQt5.QtCore import Qt, QRect, QMimeData
import os

class BetZoneWidget(QWidget):
    def __init__(self, joueur_idx, main_window=None, parent=None):
        super().__init__(parent)
        self.joueur_idx = joueur_idx
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setMinimumSize(230, 120)  # Hauteur réduite (150 -> 120)
        #self.setStyleSheet("border: 2px solid black")

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Bordure de débogage pour le pot
        painter.setPen(QPen(QColor(128, 128, 128, 128), 2, Qt.DashLine))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 12, 12)  

        
        # Affiche la pile de jetons misés
        if self.main_window:
            bet_coins = self.main_window.game.players[self.joueur_idx].bet_coins
            jetons_imgs = [
                (10, "jeton_poker_V.png"),
                (20, "jeton_poker_B.png"),
                (50, "jeton_poker_R.png"),
                (100, "jeton_poker_N.png"),
            ]
            x = 8
            jeton_size = 48
            recouvrement = 8  # moins d'espace vertical
            col_spacing = 5   # plus d'espace horizontal entre colonnes
            for idx, (value, img_name) in enumerate(jetons_imgs):
                count = bet_coins[idx] if idx < len(bet_coins) else 0
                if count == 0:
                    x += col_spacing
                    continue
                pix = QPixmap(os.path.join(os.path.dirname(__file__), "../assets", img_name)).scaled(jeton_size, jeton_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # Calcul du nombre de colonnes nécessaires pour cette couleur
                max_jetons_par_col = max(1, self.height()// recouvrement)
                nb_colonnes = (count + max_jetons_par_col - 1) // max_jetons_par_col
                for col in range(nb_colonnes):
                    jetons_this_col = min(max_jetons_par_col, count - col * max_jetons_par_col)
                    for i in range(jetons_this_col):
                        y = self.height() - 20 - (i * recouvrement)
                        painter.drawPixmap(x + col * (jeton_size + 2), y, pix)
                x += col_spacing + nb_colonnes * (jeton_size + 2)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-jeton'):
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_start_pos') and (event.buttons() & Qt.LeftButton):
            # Détermine la couleur et le nombre de jetons à retirer (similaire à JetonPileWidget)
            bet_coins = self.main_window.game.players[self.joueur_idx].bet_coins
            jetons_imgs = [
                (10, "jeton_poker_V.png"),
                (20, "jeton_poker_B.png"),
                (50, "jeton_poker_R.png"),
                (100, "jeton_poker_N.png"),
            ]
            jeton_size = 48
            recouvrement = 8
            x = 8
            for idx, (value, img_name) in enumerate(jetons_imgs):
                count = bet_coins[idx] if idx < len(bet_coins) else 0
                if count == 0:
                    x += 5
                    continue
                nb_colonnes = (count + self.height()//recouvrement - 1) // (self.height()//recouvrement)
                for col in range(nb_colonnes):
                    jetons_this_col = min(self.height()//recouvrement, count - col * (self.height()//recouvrement))
                    for i in range(jetons_this_col):
                        rect_x = x + col * (jeton_size + 2)
                        rect_y = self.height() - 20 - (i * recouvrement)
                        rect = QRect(rect_x, rect_y, jeton_size, jeton_size)
                        if rect.contains(event.pos()):
                            nb = jetons_this_col - i
                            if nb > 0:
                                mime = QMimeData()
                                # On encode l'indice de couleur pour la logique inverse
                                mime.setData('application/x-jeton-bet', f"{idx}:{nb}:{self.joueur_idx}".encode())
                                drag = QDrag(self)
                                drag.setMimeData(mime)
                                # Pixmap visuel
                                pix = QPixmap(os.path.join(os.path.dirname(__file__), "../assets", img_name)).scaled(jeton_size, jeton_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                pile_pix = QPixmap(56, jeton_size + (nb-1)*recouvrement)
                                pile_pix.fill(Qt.transparent)
                                painter = QPainter(pile_pix)
                                for j in range(nb):
                                    painter.drawPixmap(4, pile_pix.height()-jeton_size-(j*recouvrement), pix)
                                painter.end()
                                drag.setPixmap(pile_pix)
                                drag.setHotSpot(event.pos() - rect.topLeft())
                                drag.exec_(Qt.MoveAction)
                            return
                    x += nb_colonnes * (jeton_size + 2) + 5

    def dropEvent(self, event):
        data = event.mimeData().data('application/x-jeton').data().decode()
        parts = data.split(':')
        couleur, nb, joueur_idx_src = parts[0], int(parts[1]), int(parts[2])
        # Récupérer l'indice de couleur s'il est présent dans les données
        couleur_idx = int(parts[3]) if len(parts) > 3 else None
        # Ajoute les jetons à la mise temporaire de ce joueur
        if self.main_window:
            if couleur_idx is not None:
                # Utiliser l'indice de couleur si disponible
                self.main_window.miser_jetons_temp_avec_idx(couleur_idx, nb, joueur_idx_src, self.joueur_idx)
            else:
                # Fallback sur l'ancienne méthode si nécessaire
                self.main_window.miser_jetons_temp(couleur, nb, joueur_idx_src, self.joueur_idx)
        event.acceptProposedAction()
