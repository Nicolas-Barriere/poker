# Poker GUI Project

This project is a graphical user interface (GUI) for a poker game implemented in Python. The GUI allows users to interact with the poker game in a visually appealing and user-friendly manner.

## Project Structure

The project is organized as follows:

```
poker-gui
├── src
│   ├── gui
│   │   ├── main_window.py      # Main application window and layout
│   │   ├── game_view.py        # Displays the current state of the poker game
│   │   └── player_panel.py      # Manages individual player information
│   ├── core
│   │   ├── poker.py            # Existing poker game logic
│   │   └── __init__.py         # Marks core as a Python package
│   └── assets
│       └── styles.qss          # Stylesheet for GUI components
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd poker-gui
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using `venv` or `conda`. After activating your environment, run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Navigate to the `src/gui` directory and run the main window script:
   ```
   python main_window.py
   ```

## Usage Guidelines

- Upon launching the application, you will see the main window with options to start a new game, view player information, and see the current state of the game.
- Players can interact with the game through the GUI, making bets, folding, and viewing community cards.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.