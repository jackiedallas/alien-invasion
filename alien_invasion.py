import sys
import pygame  # type: ignore
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        pygame.init()

        # initialize clock method for refresh rate
        self.clock = pygame.time.Clock()

        # initialize settings from settings.py
        self.settings = Settings()
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))

        pygame.display.set_caption("Alien Invasion")
        self.ship = Ship(self)

        # initialize bullets
        self.bullets = pygame.sprite.Group()
        self.screen_rect = self.screen.get_rect()

        # initialize aliens
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

    def _create_fleet(self):
        """Create a fleet of aliens."""
        # make an alien
        alien = Alien(self)
        alien_width = alien.rect.width
        current_x = alien_width

        while current_x < (self.settings.screen_width):
            new_alien = Alien(self)
            new_alien.x = current_x
            new_alien.rect.x = current_x
            self.aliens.add(new_alien)
            current_x += 2 * alien_width

        # add the alien to the sprite group
        self.aliens.add(alien)

    def run_game(self):
        """Start main loop for game."""
        while True:
            # Watch for keyboard and mouse events
            self._check_events()

            # redraw the screen during each pass through the loop
            self._update_screen()

            # update ships position
            self.ship.update()

            # update bullets
            self._update_bullets()

            # update screen 60 times per second
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypress and mouse events."""
        for event in pygame.event.get():

            match event.type:
                case pygame.QUIT:
                    sys.exit()
                case pygame.KEYDOWN:
                    self._check_keydown_events(event)
                case pygame.KEYUP:
                    self._check_keyup_events(event)

    def _update_bullets(self):
        """Update the position of bullets and get rid of old bullets."""
        # Update the bullet positions
        self.bullets.update()

        # get rid of the bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            # if bullet.rect.left >= self.screen_rect.right:
            #     self.bullets.remove(bullet)

    def _update_screen(self):
        """Update images on the screen, and flip to new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        pygame.display.flip()

    def _check_keydown_events(self, event):
        """Respond to keypress."""
        match event.key:
            case pygame.K_RIGHT:
                self.ship.moving_right = True
            case pygame.K_LEFT:
                self.ship.moving_left = True
            case pygame.K_UP:
                self.ship.moving_up = True
            case pygame.K_DOWN:
                self.ship.moving_down = True
            case pygame.K_SPACE:
                self._fire_bullet()
            case pygame.K_q:
                sys.exit()

    def _check_keyup_events(self, event):
        """Respond to keyup events"""
        match event.key:
            case pygame.K_RIGHT:
                self.ship.moving_right = False
            case pygame.K_LEFT:
                self.ship.moving_left = False
            case pygame.K_UP:
                self.ship.moving_up = False
            case pygame.K_DOWN:
                self.ship.moving_down = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


if __name__ == '__main__':
    # make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()
