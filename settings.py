class Settings:
    """A class to store all settings for Alien Invasion"""

    def __init__(self):

        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (5, 5, 15)  # sky blue color

        # ship settings
        self.ship_speed = 4.0
        self.ship_limit = 3

        # bullet settings
        self.bullet_speed = 25
        self.bullet_width = 3
        # self.bullet_width = 15
        self.bullet_height = 15
        # self.bullet_height = 3
        self.bullet_color = (57, 255, 20)  # lime green color
        self.bullets_allowed = 5

        # star settings
        self.star_color = (245, 245, 250)  # soft white
        self.star_radius = 1

        # alien settings
        self.alien_speed = 10.0
        self.fleet_drop_speed = 15
        self.fleet_direction = 1
