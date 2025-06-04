from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QPainter, QDrag
import os

class JetonsContainerWidget(QWidget):
    def __init__(self, jetons_list, joueur_idx=None, main_window=None, parent=None):
        super().__init__(parent)
        self.joueur_idx = joueur_idx
        self.main_window = main_window
        self.jetons = jetons_list
        self.setMinimumSize(220, 120)  # Même taille que BetZoneWidget
        self.setStyleSheet("border: 5px solid #0000FF; background: rgba(255, 255, 255, 0.2);") # Bordure plus épaisse et plus visible
        # Important: l'ordre de couleurs doit correspondre à l'ordre des jetons dans la liste
        self.couleurs = ["noir", "rouge", "bleu", "vert"]
        # Important: l'ordre des jetons doit correspondre à l'ordre dans game.players[].coins
        # [noir, rouge, bleu, vert] = ordre dans Player.coins, BetZoneWidget, PotWidget
        self.jetons_imgs = [
            (10, "jeton_poker_V.png"),
            (20, "jeton_poker_B.png"),
            (50, "jeton_poker_R.png"),
            (100, "jeton_poker_N.png"),
        ]
        
        # Pour le drag and drop
        self.setMouseTracking(True)
        self.drag_start_pos = None
        self.recouvrement_drag = 40  # Même valeur que dans JetonPileWidget pour une expérience cohérente

    def paintEvent(self, event):
        painter = QPainter(self)
        
        
        x = 0
        jeton_size = 48
        recouvrement = 8  # même valeur que dans BetZoneWidget
        
        for idx, (value, img_name) in enumerate(self.jetons_imgs):
            count = self.jetons[idx] if idx < len(self.jetons) else 0
            if count == 0:
                continue
            pix = QPixmap(os.path.join(os.path.dirname(__file__), "../assets", img_name)).scaled(jeton_size, jeton_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Calcul du nombre de colonnes nécessaires pour cette couleur
            max_jetons_par_col = max(1, (self.height() - 24) // recouvrement)
            nb_colonnes = (count + max_jetons_par_col - 1) // max_jetons_par_col
            
            # Dessiner un rectangle pour chaque pile de jetons d'une couleur
            #pile_width = nb_colonnes * (jeton_size + 2)
            #painter.setPen(Qt.green)
            #painter.drawRect(x, 10, pile_width, self.height() - 20)
            
            for col in range(nb_colonnes):
                jetons_this_col = min(max_jetons_par_col, count - col * max_jetons_par_col)
                
                pile_height = jetons_this_col * recouvrement
                y_base = self.height() - pile_height

                # Dessiner un rectangle pour chaque colonne de jetons
                #painter.setPen(Qt.yellow)
                #painter.drawRect(x + col * (jeton_size + 2), y_base, jeton_size, pile_height)
                
                for i in range(jetons_this_col):
                    y = y_base + (i * recouvrement)
                    painter.drawPixmap(x + col * (jeton_size + 2), y, pix)
                x += 5 + nb_colonnes * (jeton_size + 2)  # 5 = col_spacing
                
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drag_start_pos and (event.buttons() & Qt.LeftButton):
            jeton_height = 48
            recouvrement = 8  # Pour le calcul des colonnes
            
            # Détermine quel type de jeton est sous la souris
            x = event.pos().x()
            y = event.pos().y()
            
            # Trouver quel type de jeton a été cliqué
            clicked_idx = -1
            current_x = 8
            
            for idx, (value, img_name) in enumerate(self.jetons_imgs):
                count = self.jetons[idx] if idx < len(self.jetons) else 0
                if count == 0:
                    continue
                    
                max_jetons_par_col = max(1, (self.height() - 24) // recouvrement)
                nb_colonnes = (count + max_jetons_par_col - 1) // max_jetons_par_col
                width_used = nb_colonnes * (jeton_height + 2) + 5
                
                if current_x <= x <= current_x + width_used:
                    clicked_idx = idx
                    
                    # Calcul de la colonne cliquée
                    col = min(nb_colonnes - 1, max(0, (x - current_x) // (jeton_height + 2)))
                    
                    # Calcul du nombre de jetons dans cette colonne
                    jetons_this_col = min(max_jetons_par_col, count - col * max_jetons_par_col)
                    
                    # Hauteur totale de la pile
                    pile_height = jetons_this_col * recouvrement
                    base_y = self.height() - pile_height

                    # Détermine combien de jetons prendre en fonction de la hauteur du clic
                    if y < base_y:
                        jetons_a_prendre = 0  # Clic au-dessus de la pile
                    else:
                        rel_y = y - base_y
                        # Calculer la position relative dans la pile (0 = haut, 1 = bas)
                        rel_pos = min(1.0, max(0.0, rel_y / pile_height))
                        # Plus on clique bas, plus on prend de jetons
                        jetons_a_prendre = max(1, int(rel_pos * jetons_this_col + 0.5))
                        
                    break
                    
                current_x += width_used
            
            if clicked_idx >= 0 and self.jetons[clicked_idx] > 0:
                # Utiliser l'indice directement plutôt que de se fier à la couleur
                if jetons_a_prendre > self.jetons[clicked_idx]:
                    jetons_a_prendre = self.jetons[clicked_idx]
                
                couleur = self.couleurs[clicked_idx]  # Récupérer la couleur par l'indice
                
                mime = QMimeData()
                # Format: couleur:nombre_de_jetons:joueur_idx:indice_couleur
                # L'ajout de l'indice de couleur permet d'assurer la cohérence
                mime.setData('application/x-jeton', f"{couleur}:{jetons_a_prendre}:{self.joueur_idx}:{clicked_idx}".encode())
                drag = QDrag(self)
                drag.setMimeData(mime)
                
                # Image pour le drag: utiliser la bonne image pour la couleur
                img_path = os.path.join(os.path.dirname(__file__), "../assets", self.jetons_imgs[clicked_idx][1])
                
                # Créer une image de pile si on prend plusieurs jetons
                if jetons_a_prendre > 1:
                    pix_single = QPixmap(img_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    # Augmenter la hauteur de la pile pour tenir compte du nombre de jetons
                    pile_pix = QPixmap(56, 48 + (jetons_a_prendre-1)*8)
                    pile_pix.fill(Qt.transparent)
                    painter = QPainter(pile_pix)
                    for i in range(jetons_a_prendre):
                        painter.drawPixmap(4, pile_pix.height()-48-(i*8), pix_single)
                    painter.end()
                    drag.setPixmap(pile_pix)
                else:
                    # Un seul jeton
                    pix = QPixmap(img_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    drag.setPixmap(pix)
                
                drag.setHotSpot(event.pos())
                drag.exec_(Qt.MoveAction)
                
            self.drag_start_pos = None
