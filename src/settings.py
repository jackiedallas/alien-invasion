# from game_stats import GameStats


class Settings:
    """A class to store all settings for Alien Invasion"""

    def __init__(self):

        # scoring settings
        # how quickly the aline point value increases
        self.score_scale = 1.5

        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (5, 5, 15)  # sky blue color

        # ship settings
        self.ship_limit = 3

        # bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (57, 255, 20)  # lime green color
        self.bullets_allowed = 100

        # star settings
        self.star_color = (245, 245, 250)  # soft white
        self.star_radius = 1

        # alien settings
        self.fleet_drop_speed = 5

        # how quickly the game speeds up
        self.speedup_scale = 1.1

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize the settings that can change throughout out the game."""
        self.ship_speed = 10.5
        self.bullet_speed = 5.5
        self.alien_speed = 10.0
        self.alien_points = 50

        # fleet direction of 1 represents right; -1 represents left
        self.fleet_direction = 1

    def increase_speed(self):
        """Increase speed settings."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
