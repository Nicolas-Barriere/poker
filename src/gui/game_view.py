from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget
from PyQt5.QtCore import Qt

class GameView(QWidget):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Poker Game")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.community_cards_label = QLabel("Community Cards: ")
        layout.addWidget(self.community_cards_label)

        self.player_hands_label = QLabel("Player Hands: ")
        layout.addWidget(self.player_hands_label)

        self.pot_label = QLabel("Pot: 0")
        layout.addWidget(self.pot_label)

        self.players_list = QListWidget()
        layout.addWidget(self.players_list)

        self.action_button = QPushButton("Take Action")
        self.action_button.clicked.connect(self.take_action)
        layout.addWidget(self.action_button)

        self.setLayout(layout)

    def update_view(self):
        self.community_cards_label.setText(f"Community Cards: {self.game.table.community_cards}")
        self.pot_label.setText(f"Pot: {self.game.pot.amount}")
        self.players_list.clear()
        for player in self.game.players:
            self.players_list.addItem(str(player))

    def take_action(self):
        # Logic for taking action (e.g., betting, folding) will be implemented here
        pass