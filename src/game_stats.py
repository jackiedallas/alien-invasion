

class GameStats:
    """Track stats for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.high_score = 0
        self.settings = ai_game.settings
        self.reset_stats()

    def reset_stats(self):
        """Initialize stats that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
