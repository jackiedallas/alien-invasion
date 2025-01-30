import pygame  # type ignore


class Ship:
    """A class to help manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set it's starting position."""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        # load the ship image and get its rect
        self.image = pygame.image.load('images/ship4.bmp')
        self.rect = self.image.get_rect()

        # start each new ship at the bottom of the screen
        self.rect.midbottom = self.screen_rect.midbottom
        
        # store a float for the ships exact horizontal position
        self.x = float(self.rect.x)
        
        # movement flag; start with a ship that isn't moving
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position based on the movement flag."""
        
        # update ship's x value to not go off screen
        # setting the ship speed based on the settings file
        # update ship position based on speed settings
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        
        # update rect object from self.x    
        self.rect.x = self.x
            
    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
