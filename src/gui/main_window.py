from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QGridLayout,
    QSizePolicy,
    QSpacerItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.core.poker import Game


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poker Game")
        # Créer une partie avec 4 joueurs
        self.game = Game(["Alice (Vous)", "Nico", "Bob", "Leon"])
        self.game.reset_round()
        self.game.deal_hands()
        self.game.deal_community(3)  # Flop uniquement au début
        self.initUI()

    def initUI(self):
        central_widget = BackgroundWidget("assets/bg.jpg")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        grid = QGridLayout()
        # --- Correction pour que la grille prenne tout l'espace central ---
        grid_container = QWidget()
        grid_container.setStyleSheet("border: 2px solid red;")
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)
        grid_layout.addLayout(grid)
        main_layout.addWidget(grid_container, stretch=1)
        # --- Fin correction ---

        cards_dir = os.path.join(os.path.dirname(__file__), "assets/cards")

        # Utiliser les vraies mains des joueurs
        player_hands = [p.cards for p in self.game.players]
        # Utiliser les vraies cartes communes tirées
        community_cards = self.game.table.community_cards
        deck_img = "back.png"

        # Mapping pour convertir (valeur, couleur, symbole) en nom de fichier
        value_map = {
            "A": "A",
            "K": "K",
            "Q": "Q",
            "J": "J",
            "10": "0",
            "9": "9",
            "8": "8",
            "7": "7",
            "6": "6",
            "5": "5",
            "4": "4",
            "3": "3",
            "2": "2",
        }
        suit_map = {"spade": "S", "heart": "H", "diamond": "D", "club": "C"}

        def card_to_filename(card):
            value, color, _ = card
            return f"{value_map[value]}{suit_map[color]}.png"

        def card_label(card):
            label = QLabel()
            if isinstance(card, str):
                fname = card
            else:
                fname = card_to_filename(card)
            pixmap = QPixmap(os.path.join(cards_dir, fname))
            pixmap = pixmap.scaled(90, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            return label

        def hand_widget(cards):
            w = QWidget()
            w.setStyleSheet("border: 2px solid blue;")
            l = QHBoxLayout(w)
            l.setSpacing(5)
            for c in cards:
                l.addWidget(card_label(c))
            l.addStretch()
            return w

        # Fonction utilitaire pour afficher un montant en piles de jetons
        def jetons_widget(jetons_list):
            # jetons_list = [nb_noir, nb_rouge, nb_bleu, nb_vert]
            jetons = [
                (10, "jeton_poker_V.png"),
                (20, "jeton_poker_B.png"),
                (50, "jeton_poker_R.png"),
                (100, "jeton_poker_N.png"),
            ]
            w = QWidget()
            w.setStyleSheet("border: 2px solid green;")
            h_layout = QHBoxLayout(w)
            h_layout.setSpacing(4)
            h_layout.setContentsMargins(8, 0, 8, 0)  # Augmente la marge latérale
            for idx, (value, img_name) in enumerate(jetons):
                count = jetons_list[idx] if idx < len(jetons_list) else 0
                if count == 0:
                    continue
                pile = QWidget()
                pile.setStyleSheet("border: 1px dashed orange; margin-left:0px; margin-right:0px;")
                pile.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
                v_layout = QVBoxLayout(pile)
                v_layout.setSpacing(0)
                v_layout.setContentsMargins(0, 0, 0, 0)
                v_layout.addStretch()
                for _ in range(count):
                    lbl = QLabel()
                    pix = QPixmap(
                        os.path.join(os.path.dirname(__file__), "assets", img_name)
                    )
                    pix = pix.scaled(
                        48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    lbl.setPixmap(pix)
                    lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    v_layout.addWidget(lbl, alignment=Qt.AlignBottom)
                h_layout.addWidget(pile, alignment=Qt.AlignBottom)
            h_layout.addStretch()
            return w

        def big_label(text):
            label = QLabel(text)
            label.setStyleSheet("font-size: 22px; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            return label

        # Joueur du haut
        top_player_widget = QWidget()
        top_player_widget.setStyleSheet("border: 2px solid brown;")
        top_layout = QHBoxLayout(top_player_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(20)
        top_layout.addWidget(big_label(self.game.players[2].name))
        top_layout.addWidget(hand_widget(player_hands[2]))
        top_layout.addWidget(jetons_widget(self.game.players[2].coins))
        grid.addWidget(top_player_widget, 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Ajoute un spacer vertical en haut pour centrer le centre et les joueurs de côté
        grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 1, 2, 1)

        # Joueur de gauche (ligne 3)
        left_player_widget = QWidget()
        left_player_widget.setStyleSheet("border: 2px solid orange;")
        left_layout = QVBoxLayout(left_player_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.addWidget(big_label(self.game.players[1].name), alignment=Qt.AlignLeft)
        left_layout.addWidget(hand_widget(player_hands[1]), alignment=Qt.AlignLeft)
        left_layout.addWidget(jetons_widget(self.game.players[1].coins), alignment=Qt.AlignLeft | Qt.AlignBottom)
        left_layout.addStretch()
        grid.addWidget(left_player_widget, 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        # Joueur de droite (ligne 3)
        right_player_widget = QWidget()
        right_player_widget.setStyleSheet("border: 2px solid cyan;")
        right_layout = QVBoxLayout(right_player_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(big_label(self.game.players[3].name), alignment=Qt.AlignRight)
        right_layout.addWidget(hand_widget(player_hands[3]), alignment=Qt.AlignRight)
        right_layout.addWidget(jetons_widget(self.game.players[3].coins), alignment=Qt.AlignRight | Qt.AlignBottom)
        right_layout.addStretch()
        grid.addWidget(right_player_widget, 3, 2, alignment=Qt.AlignRight | Qt.AlignVCenter)
        # Centre : cartes communes et deck (ligne 3)
        center_widget = QWidget()
        center_widget.setStyleSheet("border: 2px solid black;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        #center_layout.setContentsMargins(0, 40, 0, 40)  # marges haut/bas augmentées
        # Cartes communes (affiche seulement celles tirées)
        comm_w = QWidget()
        comm_l = QHBoxLayout(comm_w)
        for c in community_cards:
            comm_l.addWidget(card_label(c))
        center_layout.addWidget(comm_w)
        # Deck et pot côte à côte
        deck_pot_w = QWidget()
        deck_pot_l = QHBoxLayout(deck_pot_w)
        deck_lbl = card_label(deck_img)
        pot_jetons = jetons_widget(self.game.pot.amount if isinstance(self.game.pot.amount, list) else [0,0,0,0])
        deck_pot_l.addWidget(deck_lbl)
        deck_pot_l.addSpacing(20)
        deck_pot_l.addWidget(pot_jetons)
        center_layout.addWidget(deck_pot_w, alignment=Qt.AlignCenter)
        grid.addWidget(center_widget, 3, 1, alignment=Qt.AlignVCenter | Qt.AlignHCenter)
        # Ajoute un spacer vertical entre le centre et le joueur du bas
        grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 4, 1, 2, 1)
        # Joueur du bas (ligne 6)
        bottom_player_widget = QWidget()
        bottom_player_widget.setStyleSheet("border: 2px solid purple;")
        bottom_layout = QHBoxLayout(bottom_player_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(20)
        bottom_layout.addWidget(big_label(self.game.players[0].name))
        bottom_layout.addWidget(hand_widget(player_hands[0]))
        bottom_layout.addWidget(jetons_widget(self.game.players[0].coins))
        grid.addWidget(bottom_player_widget, 6, 1, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
