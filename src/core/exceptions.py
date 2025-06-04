class PokerError(Exception):
    """Erreur générique de poker."""
    pass

class InvalidBetError(PokerError):
    """Erreur de mise invalide."""
    pass

class InconsistentBetsError(PokerError):
    """Erreur : les mises ne sont pas cohérentes."""
    pass