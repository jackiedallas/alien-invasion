class Settings:
    """A class to store all settings for Alien Invasion"""
    def __init__(self):
        
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (150, 201, 244)  # sky blue color
        
        # ship settings
        self.ship_speed = 1.5
        
        # bullet settings
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)  # gray color
