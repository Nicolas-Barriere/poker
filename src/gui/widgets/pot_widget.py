from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt
import os

class PotWidget(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Désactive le drop sur le pot
        self.setMinimumSize(200, 60)  # Hauteur réduite (80 -> 60)
        self.setStyleSheet("border: 2px solid #444; background: #eee;")
        self.jetons = [0, 0, 0, 0]  # [noir, rouge, bleu, vert]
        self.main_window = main_window  # pour callback logique métier

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Bordure de débogage pour le pot
        painter.setPen(QPen(QColor(128, 128, 128, 128), 2, Qt.DashLine))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 12, 12)  

        #painter.drawText(self.rect(), Qt.AlignCenter, "Pot")
        jetons = self.main_window.game.pot.amount if self.main_window else [0,0,0,0]
        jetons_imgs = [
            (10, "jeton_poker_V.png"),
            (20, "jeton_poker_B.png"),
            (50, "jeton_poker_R.png"),
            (100, "jeton_poker_N.png"),
        ]
        marge_gauche = 24
        espace_colonne = 36
        jeton_height = 48
        recouvrement = 8  # Augmentation du recouvrement pour empiler davantage
        pile_max_height = self.height() - 32  # laisse de la place pour le texte
        # Correction : calcule le nombre max de jetons par colonne pour ne jamais dépasser la hauteur
        if jeton_height <= recouvrement:
            max_jetons_par_col = 1
        else:
            max_jetons_par_col = max(1, 1 + (pile_max_height - jeton_height) // recouvrement)
        x = marge_gauche
        for idx, (value, img_name) in enumerate(jetons_imgs):
            count = jetons[idx] if idx < len(jetons) else 0
            if count == 0:
                x += espace_colonne
                continue
            pix = QPixmap(os.path.join(os.path.dirname(__file__), "../assets", img_name)).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Calcul du nombre de colonnes nécessaires pour cette couleur
            nb_colonnes = (count + max_jetons_par_col - 1) // max_jetons_par_col
            for col in range(nb_colonnes):
                jetons_this_col = min(max_jetons_par_col, count - col * max_jetons_par_col)
                for i in range(jetons_this_col):
                    y = self.height() - 48 - (i * recouvrement)
                    painter.drawPixmap(x, y, pix)
                x += 28  # espace entre colonnes de la même couleur
            x += 8  # espace supplémentaire entre couleurs

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-jeton'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData().data('application/x-jeton').data().decode()
        # Format: couleur:nb:joueur_idx:couleur_idx
        parts = data.split(':')
        couleur, nb = parts[0], int(parts[1])
        joueur_idx = int(parts[2]) if len(parts) > 2 else None
        couleur_idx = int(parts[3]) if len(parts) > 3 else None
        
        # Appel à la logique métier de la MainWindow
        if self.main_window:
            if couleur_idx is not None:
                # Si l'indice de couleur est disponible, utiliser la version optimisée
                self.main_window.miser_jetons_avec_idx(couleur_idx, nb, joueur_idx=joueur_idx)
            else:
                # Fallback sur l'ancienne méthode
                self.main_window.miser_jetons(couleur, nb, joueur_idx=joueur_idx)
        event.acceptProposedAction()

