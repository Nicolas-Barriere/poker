from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from src.gui.widgets.jetons_container_widget import JetonsContainerWidget
from src.gui.widgets.bet_zone_widget import BetZoneWidget

class RightPlayerWidget(QWidget):
    def __init__(self, player, joueur_idx, main_window, hand_widget, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Nom du joueur
        label = QLabel(player.name)
        label.setStyleSheet("font-size: 22px; font-weight: bold;")
        label.setAlignment(Qt.AlignRight)
        layout.addWidget(label, alignment=Qt.AlignRight)

        # Zone de mise en haut
        betzone_box = QVBoxLayout()
        betzone_box.setContentsMargins(0,0,0,0)
        betzone_box.setSpacing(2)
        betzone_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone = BetZoneWidget(joueur_idx, main_window=main_window)
        betzone_box.addWidget(betzone)
        betzone_box_w = QWidget()
        betzone_box_w.setLayout(betzone_box)
        layout.addWidget(betzone_box_w, alignment=Qt.AlignRight)
        betzone.setEnabled(player.in_game)

        # Jetons
        jetons = JetonsContainerWidget(player.coins, joueur_idx=joueur_idx, main_window=main_window)
        jetons_box = QVBoxLayout()
        jetons_box.setContentsMargins(0,0,0,0)
        jetons_box.setSpacing(0)
        jetons_box.addWidget(jetons)
        jetons_box_w = QWidget()
        jetons_box_w.setLayout(jetons_box)
        layout.addWidget(jetons_box_w, alignment=Qt.AlignRight)
        jetons.setEnabled(player.in_game)

        # Montant + bouton Fold côte à côte
        montant_fold_w = QWidget(jetons)
        montant_fold_layout = QHBoxLayout(montant_fold_w)
        montant_fold_layout.setContentsMargins(5, 5, 5, 5)
        montant_fold_layout.setSpacing(8)
        montant_label = QLabel(f"{player.get_total_coins()} €")
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setAlignment(Qt.AlignCenter)
        montant_label.setFixedHeight(25)
        montant_label.setFixedWidth(80)
        fold_btn = QPushButton("Fold")
        fold_btn.setStyleSheet("background-color: rgba(255,255,255,0.7); font-size: 14px; padding: 2px 10px;")
        fold_btn.clicked.connect(lambda: main_window.fold_player(joueur_idx))
        fold_btn.setFixedHeight(25)
        fold_btn.setFixedWidth(80)
        fold_btn.setEnabled(player.in_game)
        montant_fold_layout.addWidget(montant_label)
        montant_fold_layout.addWidget(fold_btn)
        montant_fold_w.setGeometry(5, 5, 170, 35)
        montant_fold_w.raise_()

        # Main ou indication "couché"
        if player.in_game:
            layout.addWidget(hand_widget(player.cards), alignment=Qt.AlignRight | Qt.AlignBottom)
        else:
            layout.addWidget(QLabel("(Couché)"), alignment=Qt.AlignRight | Qt.AlignBottom)

        layout.addStretch()