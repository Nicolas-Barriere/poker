import os
import requests

# Dossier de destination
CARDS_DIR = os.path.join(os.path.dirname(__file__), 'cards')
os.makedirs(CARDS_DIR, exist_ok=True)

# Valeurs et couleurs
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K']
suits = ['S', 'D', 'C', 'H']  # Spades, Diamonds, Clubs, Hearts

# Deck of Cards API URL pattern
base_url = 'https://deckofcardsapi.com/static/img/'

# Télécharger les 52 cartes
for suit in suits:
    for value in values:
        card_code = f"{value}{suit}"
        url = f"{base_url}{card_code}.png"
        dest = os.path.join(CARDS_DIR, f"{card_code}.png")
        if not os.path.exists(dest):
            r = requests.get(url)
            if r.status_code == 200:
                with open(dest, 'wb') as f:
                    f.write(r.content)
                print(f"Downloaded {card_code}.png")
            else:
                print(f"Failed to download {card_code}.png")

# Télécharger les 2 jokers
for joker in ['X1', 'X2']:
    url = f"{base_url}{joker}.png"
    dest = os.path.join(CARDS_DIR, f"{joker}.png")
    if not os.path.exists(dest):
        r = requests.get(url)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"Downloaded {joker}.png")
        else:
            print(f"Failed to download {joker}.png")

# Télécharger l'image du dos de carte
back_url = f"{base_url}back.png"
back_dest = os.path.join(CARDS_DIR, "back.png")
if not os.path.exists(back_dest):
    r = requests.get(back_url)
    if r.status_code == 200:
        with open(back_dest, 'wb') as f:
            f.write(r.content)
        print("Downloaded back.png")
    else:
        print("Failed to download back.png")
