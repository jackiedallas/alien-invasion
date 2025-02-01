import pygame
from pygame.sprite import Sprite
import random


class Star(Sprite):
    """A class to manage stars for the background."""

    def __init__(self, ai_game):
        """Initialize the star and set its position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # RGB color (e.g., (255, 255, 255))
        self.color = self.settings.star_color
        self.radius = self.settings.star_radius  # Star size

        # Random position within screen bounds
        self.x = random.randint(0, self.settings.screen_width)
        self.y = random.randint(0, self.settings.screen_height)

    def draw_star(self):
        """Draw the star as a circle to the screen."""
        pygame.draw.circle(self.screen, self.color,
                           (self.x, self.y), self.radius)
