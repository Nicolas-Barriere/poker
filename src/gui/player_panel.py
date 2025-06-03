from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

class PlayerPanel(QWidget):
    def __init__(self, player_name, initial_coins):
        super().__init__()
        self.player_name = player_name
        self.coins = initial_coins
        self.current_bet = 0
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.name_label = QLabel(f"Player: {self.player_name}")
        self.coins_label = QLabel(f"Coins: {self.coins}")
        self.bet_label = QLabel(f"Current Bet: {self.current_bet}")

        self.fold_button = QPushButton("Fold")
        self.fold_button.clicked.connect(self.fold)

        layout.addWidget(self.name_label)
        layout.addWidget(self.coins_label)
        layout.addWidget(self.bet_label)
        layout.addWidget(self.fold_button)

        self.setLayout(layout)

    def update_coins(self, amount):
        self.coins += amount
        self.coins_label.setText(f"Coins: {self.coins}")

    def update_bet(self, amount):
        self.current_bet = amount
        self.bet_label.setText(f"Current Bet: {self.current_bet}")

    def fold(self):
        # Logic for folding the player can be added here
        pass