from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from src.gui.widgets.jetons_container_widget import JetonsContainerWidget
from src.gui.widgets.bet_zone_widget import BetZoneWidget

class BottomPlayerWidget(QWidget):
    def __init__(self, player, joueur_idx, main_window, hand_widget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Nom du joueur
        label = QLabel(player.name)
        label.setStyleSheet("font-size: 22px; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Main ou indication "couché"
        if player.in_game:
            layout.addWidget(hand_widget(player.cards))
        else:
            layout.addWidget(QLabel("(Couché)"))

        # Jetons
        jetons = JetonsContainerWidget(player.coins, joueur_idx=joueur_idx, main_window=main_window)
        jetons_box_w = QWidget()
        jetons_box_w.setMinimumWidth(220)
        jetons_box_w.setMinimumHeight(150)
        container_layout = QVBoxLayout(jetons_box_w)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(jetons)

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

        # Zone de mise à côté des jetons
        betzone_box = QVBoxLayout()
        betzone_box.setContentsMargins(0,0,0,0)
        betzone_box.setSpacing(2)
        betzone_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone = BetZoneWidget(joueur_idx, main_window=main_window)
        betzone_box.addWidget(betzone)
        betzone_box_w = QWidget()
        betzone_box_w.setLayout(betzone_box)

        # Layout horizontal pour jetons + zone de mise
        jetons_betzone_hbox = QHBoxLayout()
        jetons_betzone_hbox.setContentsMargins(0,0,0,0)
        jetons_betzone_hbox.setSpacing(4)
        jetons_betzone_hbox.addWidget(jetons_box_w)
        jetons_betzone_hbox.addWidget(betzone_box_w)
        jetons_betzone_hbox.addStretch()
        jetons_betzone_w = QWidget()
        jetons_betzone_w.setLayout(jetons_betzone_hbox)
        layout.addWidget(jetons_betzone_w)