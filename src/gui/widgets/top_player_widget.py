from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from src.gui.widgets.jetons_container_widget import JetonsContainerWidget
from src.gui.widgets.bet_zone_widget import BetZoneWidget

class TopPlayerWidget(QWidget):
    def __init__(self, player, joueur_idx, main_window, hand_widget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
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
        jetons_top = JetonsContainerWidget(player.coins, joueur_idx=joueur_idx, main_window=main_window)
        jetons_top_box_w = QWidget()
        jetons_top_box_w.setMinimumWidth(220)
        jetons_top_box_w.setMinimumHeight(150)
        container_layout = QVBoxLayout(jetons_top_box_w)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(jetons_top)

        # Montant + bouton Fold
        montant_fold_w = QWidget(jetons_top)
        montant_fold_layout = QHBoxLayout(montant_fold_w)
        montant_fold_layout.setContentsMargins(5, 5, 5, 5)
        montant_fold_layout.setSpacing(8)
        montant_label = QLabel(f"{player.get_total_coins()} €")
        montant_label.setStyleSheet("background-color: rgba(255,255,255,0.7); border: 1px solid black; font-weight: bold;")
        montant_label.setAlignment(Qt.AlignCenter)
        montant_label.setFixedHeight(25)
        montant_label.setFixedWidth(80)
        fold_btn_top = QPushButton("Fold")
        fold_btn_top.setStyleSheet("background-color: rgba(255,255,255,0.7); font-size: 14px; padding: 2px 10px;")
        fold_btn_top.clicked.connect(lambda: main_window.fold_player(joueur_idx))
        fold_btn_top.setFixedHeight(25)
        fold_btn_top.setFixedWidth(80)
        fold_btn_top.setEnabled(player.in_game)
        montant_fold_layout.addWidget(montant_label)
        montant_fold_layout.addWidget(fold_btn_top)
        montant_fold_w.setGeometry(5, 5, 170, 35)
        montant_fold_w.raise_()

        # Zone de mise
        betzone_top_box = QVBoxLayout()
        betzone_top_box.setContentsMargins(0,0,0,0)
        betzone_top_box.setSpacing(2)
        betzone_top_box.addWidget(QLabel("Mise", alignment=Qt.AlignHCenter))
        betzone_top = BetZoneWidget(joueur_idx, main_window=main_window)
        betzone_top_box.addWidget(betzone_top)
        betzone_top_box_w = QWidget()
        betzone_top_box_w.setLayout(betzone_top_box)

        # Layout horizontal jetons + zone de mise
        jetons_betzone_top_hbox = QHBoxLayout()
        jetons_betzone_top_hbox.setContentsMargins(0,0,0,0)
        jetons_betzone_top_hbox.setSpacing(8)
        jetons_betzone_top_hbox.addWidget(jetons_top_box_w)
        jetons_betzone_top_hbox.addWidget(betzone_top_box_w)
        jetons_betzone_top_hbox.addStretch()
        jetons_betzone_top_w = QWidget()
        jetons_betzone_top_w.setLayout(jetons_betzone_top_hbox)
        layout.addWidget(jetons_betzone_top_w)