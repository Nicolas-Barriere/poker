from PyQt5.QtWidgets import (QMainWindow,QApplication,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QGridLayout,QSizePolicy,QSpacerItem,QMessageBox,QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.core.poker import Game
from src.gui.widgets.jetons_container_widget import JetonsContainerWidget
from src.gui.widgets.background_widget import BackgroundWidget
from src.gui.widgets.jeton_pile_widget import JetonPileWidget
from src.gui.widgets.pot_widget import PotWidget
from src.gui.widgets.bet_zone_widget import BetZoneWidget
from src.core.exceptions import InconsistentBetsError
from src.gui.widgets.top_player_widget import TopPlayerWidget
from src.gui.widgets.left_player_widget import LeftPlayerWidget
from src.gui.widgets.right_player_widget import RightPlayerWidget
from src.gui.widgets.bottom_player_widget import BottomPlayerWidget


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
        grid_container = QWidget()
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)
        grid_layout.addLayout(grid)
        main_layout.addWidget(grid_container, stretch=1)
        main_layout.setContentsMargins(4, 4, 4, 4)  # Réduction des marges du layout principal

        cards_dir = os.path.join(os.path.dirname(__file__), "assets/cards")

        player_hands = [p.cards for p in self.game.players]
        community_cards = self.game.table.community_cards
        deck_img = "back.png"

        # Mapping pour convertir (valeur, couleur, symbole) en nom de fichier
        value_map = {"A": "A","K": "K","Q": "Q","J": "J","10": "0","9": "9","8": "8","7": "7","6": "6","5": "5","4": "4","3": "3","2": "2",}
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
            l = QHBoxLayout(w)
            l.setSpacing(5)
            for c in cards:
                card_lbl = card_label(c)
                l.addWidget(card_lbl)
            l.addStretch()
            return w


        def big_label(text):
            label = QLabel(text)
            label.setStyleSheet("font-size: 22px; font-weight: bold;")  # Bordure violette pour les noms
            label.setAlignment(Qt.AlignCenter)
            return label

        
        top_player_widget = TopPlayerWidget(
            self.game.players[2],
            joueur_idx=2,
            main_window=self,
            hand_widget=hand_widget
        )

        grid.addWidget(top_player_widget, 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Ajoute un spacer vertical en haut pour centrer le centre et les joueurs de côté
        grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 1, 2, 1)

        
        left_player_widget = LeftPlayerWidget(
            self.game.players[1],
            joueur_idx=1,
            main_window=self,
            hand_widget=hand_widget
        )
        grid.addWidget(left_player_widget, 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        
        right_player_widget = RightPlayerWidget(
            self.game.players[3],
            joueur_idx=3,
            main_window=self,
            hand_widget=hand_widget
        )

        grid.addWidget(right_player_widget, 3, 2, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        # Centre : cartes communes et deck (ligne 3)
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        comm_w = QWidget()
        comm_l = QHBoxLayout(comm_w)
        for c in community_cards:
            comm_l.addWidget(card_label(c))
        center_layout.addWidget(comm_w)
        deck_pot_w = QWidget()
        deck_pot_l = QHBoxLayout(deck_pot_w)
        deck_lbl = card_label(deck_img)
        pot_widget = PotWidget(main_window=self)
        deck_pot_l.addWidget(deck_lbl)
        deck_pot_l.addSpacing(20)
        deck_pot_l.addWidget(pot_widget)
        center_layout.addWidget(deck_pot_w, alignment=Qt.AlignCenter)
        grid.addWidget(center_widget, 3, 1, alignment=Qt.AlignVCenter | Qt.AlignHCenter)
        
        
        bottom_player_widget = BottomPlayerWidget(
            self.game.players[0],
            joueur_idx=0,
            main_window=self,
            hand_widget=hand_widget
        )

        # Joueur du bas repositionné à la ligne 4 pour meilleur équilibre visuel
        grid.addWidget(bottom_player_widget, 4, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)  # Aligné en haut plutôt qu'au centre
        # Spacer réduit SOUS le joueur du bas
        grid.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed), 5, 1, 1, 1)  # Hauteur fixe de 10px
        # --- Ajout du bouton de validation des mises ---
        valider_btn = QPushButton("Valider les mises")
        valider_btn.setStyleSheet("font-size: 16px; padding: 5px 20px; font-weight: bold;")  # Réduction de la taille et du padding
        valider_btn.clicked.connect(self.valider_mises)
        grid.addWidget(valider_btn, 0, 0, alignment=Qt.AlignLeft | Qt.AlignTop)
    
    def closeEvent(self, event):
        event.accept()

    def fold_player(self, joueur_idx):
        joueur = self.game.players[joueur_idx]
        joueur.fold()
        self.initUI()

    def miser_jetons(self, couleur, nb, joueur_idx=None):
        # Trouver le joueur source (par défaut joueur du bas)
        if joueur_idx is None:
            joueur = self.game.players[0]
        else:
            joueur = self.game.players[joueur_idx]
        idx = {"noir":0, "rouge":1, "bleu":2, "vert":3}[couleur]
        if joueur.coins[idx] < nb:
            return  # Sécurité
        joueur.coins[idx] -= nb
        # Ajoute au pot métier
        if isinstance(self.game.pot.amount, list):
            self.game.pot.amount[idx] += nb
        else:
            self.game.pot.amount = [0,0,0,0]
            self.game.pot.amount[idx] = nb
        self.initUI()
        
    def miser_jetons_avec_idx(self, couleur_idx, nb, joueur_idx=None):
        """Version améliorée qui utilise directement l'indice de couleur pour le pot."""
        # Trouver le joueur source (par défaut joueur du bas)
        if joueur_idx is None:
            joueur = self.game.players[0]
        else:
            joueur = self.game.players[joueur_idx]
            
        # Vérifier que l'indice est valide
        if couleur_idx < 0 or couleur_idx >= len(joueur.coins):
            print(f"Erreur: indice de couleur invalide: {couleur_idx}")
            return
            
        if joueur.coins[couleur_idx] < nb:
            return  # Sécurité
            
        # Retirer les jetons du joueur
        joueur.coins[couleur_idx] -= nb
        
        # Ajouter au pot
        if isinstance(self.game.pot.amount, list):
            self.game.pot.amount[couleur_idx] += nb
        else:
            self.game.pot.amount = [0,0,0,0]
            self.game.pot.amount[couleur_idx] = nb
            
        self.initUI()

    def miser_jetons_temp(self, couleur, nb, joueur_idx_src, joueur_idx_dest):
        # Retire les jetons du joueur source et les ajoute à la mise temporaire du joueur cible
        joueur_src = self.game.players[joueur_idx_src]
        joueur_dest = self.game.players[joueur_idx_dest]
        idx = {"noir":0, "rouge":1, "bleu":2, "vert":3}[couleur]
        if joueur_src.coins[idx] < nb:
            return
        joueur_src.coins[idx] -= nb
        if not hasattr(joueur_dest, 'bet_coins') or joueur_dest.bet_coins is None:
            joueur_dest.bet_coins = [0,0,0,0]
        joueur_dest.bet_coins[idx] += nb
        self.initUI()
        
    def miser_jetons_temp_avec_idx(self, couleur_idx, nb, joueur_idx_src, joueur_idx_dest):
        # Version améliorée qui utilise directement l'indice de couleur
        joueur_src = self.game.players[joueur_idx_src]
        joueur_dest = self.game.players[joueur_idx_dest]
        
        # Vérifier que l'indice est valide
        if couleur_idx < 0 or couleur_idx >= len(joueur_src.coins):
            print(f"Erreur: indice de couleur invalide: {couleur_idx}")
            return
            
        if joueur_src.coins[couleur_idx] < nb:
            return
            
        # Retirer les jetons du joueur source
        joueur_src.coins[couleur_idx] -= nb
        
        # Ajouter les jetons à la mise temporaire du joueur cible
        if not hasattr(joueur_dest, 'bet_coins') or joueur_dest.bet_coins is None:
            joueur_dest.bet_coins = [0,0,0,0]
        joueur_dest.bet_coins[couleur_idx] += nb
        
        self.initUI()

    def valider_mises(self):
        try:
            self.game.validate_bets()
        except InconsistentBetsError as e:
            QMessageBox.warning(self, "Erreur de mise", str(e))
            return
        self.transfer_bets_to_pot()


    def transfer_bets_to_pot(self):
        # Transfère toutes les mises (bet_coins) dans le pot
        for idx, joueur in enumerate(self.game.players):
            for color_idx in range(4):
                nb = joueur.bet_coins[color_idx] if hasattr(joueur, 'bet_coins') else 0
                if nb > 0:
                    if isinstance(self.game.pot.amount, list):
                        self.game.pot.amount[color_idx] += nb
                    else:
                        self.game.pot.amount = [0,0,0,0]
                        self.game.pot.amount[color_idx] = nb
                    joueur.bet_coins[color_idx] = 0
        self.next_round()

    def next_round(self):
        # Retourne une carte commune si possible, sinon compare les mains
        nb_community = len(self.game.table.community_cards)
        if nb_community < 5:
            self.game.deal_community(1)
            self.initUI()
        else:
            # Fin du coup : on compare les mains et affiche le vainqueur
            gagnant, main_gagnante = self.game.get_winner()
            msg = QMessageBox(self)
            msg.setWindowTitle("Résultat de la main")
            msg.setText(f"Le gagnant est {gagnant.name} avec {main_gagnante} !")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self.initUI()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
