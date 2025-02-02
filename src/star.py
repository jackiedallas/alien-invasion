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
        self.color = self.settings.star_color
        self.radius = self.settings.star_radius  # Star size

        # Create a small transparent surface
        self.image = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color,
                           (self.radius, self.radius), self.radius)

        # Set position randomly
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, self.settings.screen_width)
        self.rect.y = random.randint(0, self.settings.screen_height)

    def draw_star(self):
        """Draw the star using its rect attribute."""
        self.screen.blit(self.image, self.rect)
