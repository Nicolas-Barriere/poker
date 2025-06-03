# filepath: /poker-gui/poker-gui/src/core/poker.py
import random
from treys import Card, Evaluator


class Player:
    def __init__(self, name, coins=[4, 6, 8, 10]):
        self.name = name
        self.cards = []
        self.coins = coins
        self.in_game = True
        self.current_bet = 0

    def fold(self):
        self.in_game = False
        print(f"{self.name} se couche.")

    def get_amount(self):
        # coins = [noir, rouge, bleu, vert]
        return 100*self.coins[0] + 50*self.coins[1] + 20*self.coins[2] + 10*self.coins[3]

    def bet(self, jetons):
        # jetons = [noir, rouge, bleu, vert]
        if any(j > c for j, c in zip(jetons, self.coins)):
            raise ValueError(f"{self.name} n'a pas assez de jetons pour miser {jetons}.")
        for i in range(4):
            self.coins[i] -= jetons[i]
        self.current_bet += 100*jetons[0] + 50*jetons[1] + 20*jetons[2] + 10*jetons[3]
        print(f"{self.name} mise {jetons} => reste: {self.coins}")

    def receive_jetons(self, jetons):
        # Ajoute une liste de jetons [noir, rouge, bleu, vert]
        for i in range(4):
            self.coins[i] += jetons[i]

    def reset_for_round(self):
        self.cards = []
        self.in_game = True
        self.current_bet = 0
        # Les jetons ne sont pas réinitialisés ici

    def receive_card(self, card):
        self.cards.append(card)

    def __str__(self):
        return f"{self.name} | Jetons: {self.coins} | Cartes: {self.cards} | En jeu: {self.in_game}"


class Deck:
    def __init__(self):
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = [("heart", "♥"), ("spade", "♠"), ("diamond", "♦"), ("club", "♣")]
        self.cards = [
            (value, color, symbol) for value in values for color, symbol in suits
        ]
        random.shuffle(self.cards)

    def distribute(self, players):
        i = 0
        n = len(players)
        while self.cards:
            players[i % n].append(self.cards.pop())

    def draw(self):
        if not self.cards:
            raise ValueError("Le paquet est vide.")
        return self.cards.pop()

    def reset(self):
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = [("heart", "♥"), ("spade", "♠"), ("diamond", "♦"), ("club", "♣")]
        self.cards = [
            (value, color, symbol) for value in values for color, symbol in suits
        ]
        random.shuffle(self.cards)

    def is_empty(self):
        return len(self.cards) == 0

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck: {len(self.cards)} cartes restantes"


class Table:
    def __init__(self):
        self.community_cards = []
        self.pot = [0, 0, 0, 0]  # [noir, rouge, bleu, vert]
        self.dealer_pos = 0

    def reset(self):
        self.community_cards = []
        self.pot = [0, 0, 0, 0]

    def add_to_pot(self, jetons):
        # jetons = [noir, rouge, bleu, vert]
        for i in range(4):
            self.pot[i] += jetons[i]

    def __str__(self):
        return f"Table | Pot: {self.pot} | Cartes communes: {self.community_cards}"


class HandEvaluator:
    @staticmethod
    def evaluate_hand(player_cards, community_cards):
        def to_treys(card):
            value, color, _ = card
            value_map = {
                "2": "2",
                "3": "3",
                "4": "4",
                "5": "5",
                "6": "6",
                "7": "7",
                "8": "8",
                "9": "9",
                "10": "T",
                "J": "J",
                "Q": "Q",
                "K": "K",
                "A": "A",
            }
            suit_map = {"spade": "s", "heart": "h", "diamond": "d", "club": "c"}
            return value_map[value] + suit_map[color]

        treys_player = [Card.new(to_treys(c)) for c in player_cards]
        treys_community = [Card.new(to_treys(c)) for c in community_cards]
        evaluator = Evaluator()
        score = evaluator.evaluate(treys_player, treys_community)
        class_name = evaluator.class_to_string(evaluator.get_rank_class(score))
        return (
            -score,
            class_name,
        )


class Pot:
    def __init__(self):
        self.amount = [0, 0, 0, 0]  # [noir, rouge, bleu, vert]
        self.side_pots = []

    def add(self, jetons):
        for i in range(4):
            self.amount[i] += jetons[i]

    def reset(self):
        self.amount = [0, 0, 0, 0]
        self.side_pots = []

    def __str__(self):
        return f"Pot principal: {self.amount}, Side pots: {self.side_pots}"


class Dealer:
    def __init__(self, num_players):
        self.position = 0
        self.num_players = num_players

    def next(self):
        self.position = (self.position + 1) % self.num_players
        return self.position

    def __str__(self):
        return f"Dealer position: {self.position}"


class Game:
    def __init__(self, player_names, starting_coins=[4,6,8,10]):
        self.players = [Player(name, starting_coins[:]) for name in player_names]
        self.deck = Deck()
        self.table = Table()
        self.pot = Pot()
        self.dealer = Dealer(len(self.players))
        self.current_bet = 0
        self.active_players = self.players.copy()

    def reset_round(self):
        self.deck.reset()
        self.table.reset()
        self.pot.reset()
        for player in self.players:
            player.reset_for_round()
        self.active_players = [p for p in self.players if sum(p.coins) > 0]
        self.current_bet = 0

    def deal_hands(self, cards_per_player=2):
        for _ in range(cards_per_player):
            for player in self.active_players:
                player.receive_card(self.deck.draw())

    def deal_community(self, n):
        for _ in range(n):
            card = self.deck.draw()
            self.table.community_cards.append(card)

    def set_blinds(self, small_blind=[0,0,0,1], big_blind=[0,0,0,2]):
        sb_pos = self.dealer.position % len(self.active_players)
        bb_pos = (self.dealer.position + 1) % len(self.active_players)
        sb_player = self.active_players[sb_pos]
        bb_player = self.active_players[bb_pos]
        # On suppose que small_blind et big_blind sont des listes de jetons
        sb_player.bet(10*small_blind[3] + 20*small_blind[2] + 50*small_blind[1] + 100*small_blind[0])
        bb_player.bet(10*big_blind[3] + 20*big_blind[2] + 50*big_blind[1] + 100*big_blind[0])
        self.pot.add(small_blind)
        self.pot.add(big_blind)
        self.current_bet = 10*big_blind[3] + 20*big_blind[2] + 50*big_blind[1] + 100*big_blind[0]
        print(
            f"Small blind: {sb_player.name} ({small_blind}) | Big blind: {bb_player.name} ({big_blind})"
        )

    def betting_round(self):
        to_call = self.current_bet
        for player in self.active_players:
            if player.in_game and player.coins > 0:
                if player.name == "Nico":
                    print(f"\n{player.name}, c'est à vous de jouer !")
                    print(f"Vos cartes : {player.cards}")
                    print(f"Cartes communes : {self.table.community_cards}")
                    print(f"Jetons restants : {player.coins}")
                    print(f"Mise à suivre : {to_call}")
                    action = (
                        input(
                            "Action ([c]heck, [f]old, [a]ll-in, [s]uivre/call, [r]aise) : "
                        )
                        .strip()
                        .lower()
                    )
                    if action == "f":
                        player.fold()
                    elif action == "a":
                        self.pot.add(player.coins)
                        player.bet(player.coins)
                    elif action == "r":
                        amount = int(input("Montant de la relance : "))
                        total_bet = to_call + amount
                        player.bet(total_bet)
                        self.pot.add(total_bet)
                        self.current_bet = total_bet
                    elif action == "s":
                        call_amt = to_call - player.current_bet
                        player.bet(call_amt)
                        self.pot.add(call_amt)
                    else:
                        player.check()
                else:
                    call_amt = to_call - player.current_bet
                    if call_amt > 0 and player.coins >= call_amt:
                        player.bet(call_amt)
                        self.pot.add(call_amt)
                    else:
                        player.check()

    def play_round(self):
        self.reset_round()
        self.deal_hands()
        print("--- Distribution des mains ---")
        for p in self.players:
            print(p)
        self.set_blinds()
        self.betting_round()
        self.deal_community(3)
        print(f"Flop: {self.table.community_cards}")
        self.betting_round()
        self.deal_community(1)
        print(f"Turn: {self.table.community_cards[-1]}")
        self.betting_round()
        self.deal_community(1)
        print(f"River: {self.table.community_cards[-1]}")
        self.betting_round()
        print("--- Showdown ---")
        in_game = [p for p in self.active_players if p.in_game]
        best_score = -float("inf")
        winners = []
        for p in in_game:
            score, desc = HandEvaluator.evaluate_hand(
                p.cards, self.table.community_cards
            )
            print(f"{p.name}: {p.cards} + {self.table.community_cards} => {desc}")
            if score > best_score:
                best_score = score
                winners = [p]
            elif score == best_score:
                winners.append(p)
        if winners:
            for w in winners:
                w.coins += self.pot.amount // len(winners)
            print(
                f"Gagnant(s) : {', '.join([w.name for w in winners])} remporte(nt) le pot de {self.pot.amount} jetons !"
            )
        else:
            print("Personne ne remporte le pot.")

    def play(self, num_rounds=1):
        for i in range(num_rounds):
            print(f"\n=== Manche {i+1} ===")
            self.play_round()


class Strategy:
    pass


class Profile:
    pass