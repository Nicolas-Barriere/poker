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

        # Joueur du haut
        top_player_widget = QWidget()
        top_layout = QHBoxLayout(top_player_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(20)
        top_layout.addWidget(big_label(self.game.players[2].name))
        
        if self.game.players[2].in_game:
            top_layout.addWidget(hand_widget(player_hands[2]))
        else:
            top_layout.addWidget(QLabel("(Couché)"))
        jetons_top = JetonsContainerWidget(self.game.players[2].coins, joueur_idx=2, main_window=self)
        jetons_top_box_w = QWidget()
        jetons_top_box_w.setMinimumWidth(220)
        jetons_top_box_w.setMinimumHeight(150)

        # Layout avec contenu
        container_layout = QVBoxLayout(jetons_top_box_w)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(jetons_top)
        
        montant_fold_w = QWidget(jetons_top)
        montant_fold_layout = QHBoxLayout(montant_fold_w)
        montant_fold_layout.setContentsMargins(5, 5, 5, 5)
        montant_fold_layout.setSpacing(8)

        montant_label = QLabel(f"{self.game.players[2].get_total_coins()} €")
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setAlignment(Qt.AlignCenter)
        montant_label.setFixedHeight(25)
        montant_label.setFixedWidth(80)

        fold_btn_top = QPushButton("Fold")
        fold_btn_top.setStyleSheet("background-color: rgba(255,255,255,0.7); font-size: 14px; padding: 2px 10px;")
        fold_btn_top.clicked.connect(lambda: self.fold_player(2))
        fold_btn_top.setFixedHeight(25)
        fold_btn_top.setFixedWidth(80)


        montant_fold_layout.addWidget(montant_label)
        montant_fold_layout.addWidget(fold_btn_top)

        # Positionne le widget en overlay sur le widget des jetons
        montant_fold_w.setGeometry(5, 5, 170, 35)
        montant_fold_w.raise_()

        # Ajout de la zone de mise à côté des jetons
        betzone_top_box = QVBoxLayout()
        betzone_top_box.setContentsMargins(0,0,0,0)
        betzone_top_box.setSpacing(2)
        betzone_top_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone_top = BetZoneWidget(2, main_window=self)
        betzone_top_box.addWidget(betzone_top)
        betzone_top_box_w = QWidget()
        betzone_top_box_w.setLayout(betzone_top_box)
        #betzone_top_box_w.setStyleSheet("border: 2px solid #8B4513;")  # Bordure marron pour conteneur betzone
        # Layout horizontal pour jetons + zone de mise
        jetons_betzone_top_hbox = QHBoxLayout()
        jetons_betzone_top_hbox.setContentsMargins(0,0,0,0)
        jetons_betzone_top_hbox.setSpacing(8)
        jetons_betzone_top_hbox.addWidget(jetons_top_box_w)
        jetons_betzone_top_hbox.addWidget(betzone_top_box_w)
        jetons_betzone_top_hbox.addStretch()
        jetons_betzone_top_w = QWidget()
        jetons_betzone_top_w.setLayout(jetons_betzone_top_hbox)
        #jetons_betzone_top_w.setStyleSheet("border: 2px solid #FF69B4;")  # Bordure rose pour conteneur jetons+betzone
        top_layout.addWidget(jetons_betzone_top_w)

        grid.addWidget(top_player_widget, 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Ajoute un spacer vertical en haut pour centrer le centre et les joueurs de côté
        grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 1, 2, 1)

        # Joueur de gauche (ligne 3)
        left_player_widget = QWidget()
        left_layout = QVBoxLayout(left_player_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(3)  # Réduction de l'espacement (6 -> 3)
        left_layout.addWidget(big_label(self.game.players[1].name), alignment=Qt.AlignLeft)
        
        # Ajout de la zone de mise en haut
        betzone_left_box = QVBoxLayout()
        betzone_left_box.setContentsMargins(0,0,0,0)
        betzone_left_box.setSpacing(2)
        betzone_left_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone_left = BetZoneWidget(1, main_window=self)
        betzone_left_box.addWidget(betzone_left)
        betzone_left_box_w = QWidget()
        betzone_left_box_w.setLayout(betzone_left_box)
        left_layout.addWidget(betzone_left_box_w, alignment=Qt.AlignLeft)
        
        # Ajout des jetons au milieu avec JetonsContainerWidget
        jetons_left = JetonsContainerWidget(self.game.players[1].coins, joueur_idx=1, main_window=self)
        jetons_left_box = QVBoxLayout()
        jetons_left_box.setContentsMargins(0,0,0,0)
        jetons_left_box.setSpacing(0)  # Réduit l'espacement à 0 (au lieu de 2)
        jetons_left_box.addWidget(jetons_left)
        
        # Ajouter le montant directement sur le widget des jetons
        montant_label = QLabel(f"{self.game.players[1].get_total_coins()} €", jetons_left)
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setGeometry(5, 5, 80, 25)
        montant_label.setAlignment(Qt.AlignCenter)

        jetons_left_box_w = QWidget()
        jetons_left_box_w.setLayout(jetons_left_box)
        #jetons_left_box_w.setStyleSheet("border: 2px solid #32CD32;")  # Bordure vert lime pour conteneur jetons
        left_layout.addWidget(jetons_left_box_w, alignment=Qt.AlignLeft)
        
        # Ajout des cartes en bas
        left_layout.addWidget(hand_widget(player_hands[1]), alignment=Qt.AlignLeft | Qt.AlignBottom)
        left_layout.addStretch()
        grid.addWidget(left_player_widget, 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        # Joueur de droite (ligne 3)
        right_player_widget = QWidget()
        #right_player_widget.setStyleSheet(player_border)  # Bordure turquoise pour joueur de droite
        right_layout = QVBoxLayout(right_player_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(3)  # Réduction de l'espacement (6 -> 3)
        right_layout.addWidget(big_label(self.game.players[3].name), alignment=Qt.AlignRight)
        
        # Ajout de la zone de mise en haut
        betzone_right_box = QVBoxLayout()
        betzone_right_box.setContentsMargins(0,0,0,0)
        betzone_right_box.setSpacing(2)
        betzone_right_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone_right = BetZoneWidget(3, main_window=self)
        betzone_right_box.addWidget(betzone_right)
        betzone_right_box_w = QWidget()
        betzone_right_box_w.setLayout(betzone_right_box)
        #betzone_right_box_w.setStyleSheet("border: 2px solid #8B4513;")  # Bordure marron pour conteneur betzone
        right_layout.addWidget(betzone_right_box_w, alignment=Qt.AlignRight)
        
        # Ajout des jetons au milieu avec JetonsContainerWidget
        jetons_right = JetonsContainerWidget(self.game.players[3].coins, joueur_idx=3, main_window=self)
        jetons_right_box = QVBoxLayout()
        jetons_right_box.setContentsMargins(0,0,0,0)
        jetons_right_box.setSpacing(0)  # Réduit l'espacement à 0 (au lieu de 2)
        jetons_right_box.addWidget(jetons_right)
        
        # Ajouter le montant directement sur le widget des jetons
        montant_label = QLabel(f"{self.game.players[3].get_total_coins()} €", jetons_right)
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setGeometry(5, 5, 80, 25)
        montant_label.setAlignment(Qt.AlignCenter)

        jetons_right_box_w = QWidget()
        jetons_right_box_w.setLayout(jetons_right_box)
        #jetons_right_box_w.setStyleSheet("border: 2px solid #32CD32;")  # Bordure vert lime pour conteneur jetons
        right_layout.addWidget(jetons_right_box_w, alignment=Qt.AlignRight)
        
        # Ajout des cartes en bas
        right_layout.addWidget(hand_widget(player_hands[3]), alignment=Qt.AlignRight | Qt.AlignBottom)
        right_layout.addStretch()
        grid.addWidget(right_player_widget, 3, 2, alignment=Qt.AlignRight | Qt.AlignVCenter)
        # Centre : cartes communes et deck (ligne 3)
        center_widget = QWidget()
        #center_widget.setStyleSheet(center_border)  # Bordure orange pour le centre
        center_layout = QVBoxLayout(center_widget)
        comm_w = QWidget()
        comm_l = QHBoxLayout(comm_w)
        for c in community_cards:
            comm_l.addWidget(card_label(c))
        center_layout.addWidget(comm_w)
        # Deck et pot côte à côte
        deck_pot_w = QWidget()
        deck_pot_l = QHBoxLayout(deck_pot_w)
        deck_lbl = card_label(deck_img)
        pot_widget = PotWidget(main_window=self)
        deck_pot_l.addWidget(deck_lbl)
        deck_pot_l.addSpacing(20)
        deck_pot_l.addWidget(pot_widget)
        center_layout.addWidget(deck_pot_w, alignment=Qt.AlignCenter)
        grid.addWidget(center_widget, 3, 1, alignment=Qt.AlignVCenter | Qt.AlignHCenter)
        
        # Pas de spacer entre le centre et le joueur du bas pour maximiser l'espace
        # Joueur du bas (ligne 4)
        bottom_player_widget = QWidget()
        #bottom_player_widget.setStyleSheet(player_border)  # Bordure turquoise pour joueur du bas
        bottom_layout = QHBoxLayout(bottom_player_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        bottom_layout.addWidget(big_label(self.game.players[0].name))
        bottom_layout.addWidget(hand_widget(player_hands[0]))
        
        # Utilisation de JetonsContainerWidget au lieu de jetons_widget
        # Container directement intégré avec montant placé en superposition
        jetons_bottom = JetonsContainerWidget(self.game.players[0].coins, joueur_idx=0, main_window=self)
        # Créer un QWidget pour encadrer le contenu
        jetons_bottom_box_w = QWidget()
        jetons_bottom_box_w.setMinimumWidth(220)
        jetons_bottom_box_w.setMinimumHeight(150)
        #jetons_bottom_box_w.setStyleSheet("border: 4px solid #FF00FF;") # Bordure magenta visible
        
        # Layout avec contenu
        container_layout = QVBoxLayout(jetons_bottom_box_w)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(jetons_bottom)
        
        # Ajouter le montant directement sur le widget des jetons
        montant_label = QLabel(f"{self.game.players[0].get_total_coins()} €", jetons_bottom)
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setGeometry(5, 5, 80, 25)
        montant_label.setAlignment(Qt.AlignCenter)
        # Ajout de la zone de mise à côté des jetons
        betzone_bottom_box = QVBoxLayout()
        betzone_bottom_box.setContentsMargins(0,0,0,0)
        betzone_bottom_box.setSpacing(2)
        betzone_bottom_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone_bottom = BetZoneWidget(0, main_window=self)
        betzone_bottom_box.addWidget(betzone_bottom)
        betzone_bottom_box_w = QWidget()
        betzone_bottom_box_w.setLayout(betzone_bottom_box)
        #betzone_bottom_box_w.setStyleSheet("border: 2px solid #8B4513;")  # Bordure marron pour conteneur betzone
        # Layout horizontal pour jetons + zone de mise
        jetons_betzone_bottom_hbox = QHBoxLayout()
        jetons_betzone_bottom_hbox.setContentsMargins(0,0,0,0)
        jetons_betzone_bottom_hbox.setSpacing(4)  # Réduction de l'espacement (8 -> 4)
        jetons_betzone_bottom_hbox.addWidget(jetons_bottom_box_w)
        jetons_betzone_bottom_hbox.addWidget(betzone_bottom_box_w)
        jetons_betzone_bottom_hbox.addStretch()
        jetons_betzone_bottom_w = QWidget()
        jetons_betzone_bottom_w.setLayout(jetons_betzone_bottom_hbox)
        #jetons_betzone_bottom_w.setStyleSheet("border: 2px solid #FF69B4;")  # Bordure rose pour conteneur jetons+betzone
        bottom_layout.addWidget(jetons_betzone_bottom_w)
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
