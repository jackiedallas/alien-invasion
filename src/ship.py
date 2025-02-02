import pygame  # type ignore
from pathlib import Path

current_dir = Path(__file__).resolve().parent
ship_path = f"{current_dir}/images/ship.bmp"


class Ship:
    """A class to help manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set it's starting position."""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        # load the ship image and get its rect
        self.image = pygame.image.load(ship_path)
        self.rect = self.image.get_rect()

        # start each new ship at the bottom of the screen
        self.rect.midbottom = self.screen_rect.midbottom
        # self.rect.midleft = self.screen_rect.midleft

        # store a float for the ships exact horizontal/vertical position
        self.x = float(self.rect.x)
        # self.y = float(self.rect.y)

        # movement flag; start with a ship that isn't moving
        self.moving_right = False
        self.moving_left = False
        # self.moving_up = False
        # self.moving_down = False

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on the movement flag."""

        # update ship's x value to not go off screen
        # setting the ship speed based on the settings file
        # update ship position based on speed settings
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.rect.right < \
                self.screen.get_rect().right:
            self.x += self.settings.ship_speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        # if self.moving_right and self.rect.right < self.screen_rect.right:
        #     self.x += self.settings.ship_speed
        # if self.moving_left and self.rect.left > 0:
        #     self.x -= self.settings.ship_speed
        # if self.moving_up and self.rect.top > self.screen_rect.top:
        #     self.y -= self.settings.ship_speed
        # if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
        #     self.y += self.settings.ship_speed

        # update rect object from self.x
        self.rect.x = self.x
        # self.rect.y = self.y

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
