import sys
from pathlib import Path
from time import sleep
import pygame  # type: ignore
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard

current_dir = Path(__file__).resolve().parent
laser_path = f"{current_dir}/sounds/laser.wav"
explosion_path = f"{current_dir}/sounds/explosion.wav"


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        pygame.init()

        # initialize mixer for sound
        pygame.mixer.init()
        self.laser_sound = pygame.mixer.Sound(laser_path)
        self.explosion_sound = pygame.mixer.Sound(explosion_path)

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

        # initialize stars
        self.stars = pygame.sprite.Group()
        self._create_star()

        # initialize game stats
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)

        # start alien invasion in an inactive state
        self.game_active = False

        # initialize the play button
        self.play_button = Button(self, "Play")

    def _check_aliens_bottom(self):
        """Check if any aliens reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # decrement ships_left.
            self.stats.ships_left -= 1

            # get rid of any remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()

            # create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()

            # pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _create_star(self):
        """Create a background of stars."""
        for _ in range(1000):
            star = Star(self)
            self.stars.add(star)

    def _create_fleet(self):
        """Create a fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left
        # Spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height

        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

        # add the alien to the sprite group
        self.aliens.add(alien)

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond correctly if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and chagne the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

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
                case pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            self._start_game()

    def _start_game(self):
        """start the game"""
        # reset game stats
        self.stats.reset_stats()
        self.game_active = True

        # Get rid of any remaining bullets and aliens
        self.bullets.empty()
        self.aliens.empty()

        # create new fleet and center
        self._create_fleet()
        self.ship.center_ship()

        # hide the mouse cursor
        pygame.mouse.set_visible(False)

    def _update_bullets(self):
        """Update the position of bullets and get rid of old bullets."""
        # Update the bullet positions
        self.bullets.update()

        # get rid of the bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # check for any bullets that have hit aliens.
        # if so, get rid of the bullet and the alien
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.explosion_sound.play()

        if not self.aliens:
            # destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _update_screen(self):
        """Update images on the screen, and flip to new screen."""
        self.screen.fill(self.settings.bg_color)
        for star in self.stars:
            star.draw_star()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _check_keydown_events(self, event):
        """Respond to keypress."""
        match event.key:
            case pygame.K_RIGHT:
                self.ship.moving_right = True
            case pygame.K_LEFT:
                self.ship.moving_left = True
            case pygame.K_p:
                if self.game_active is False:
                    self._start_game()
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
            # case pygame.K_UP:
            #     self.ship.moving_up = False
            # case pygame.K_DOWN:
            #     self.ship.moving_down = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.laser_sound.play()

    def _update_aliens(self):
        """check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def run_game(self):
        """Start main loop for game."""
        while True:
            # Watch for keyboard and mouse events
            self._check_events()

            if self.game_active:
                # update ships position
                self.ship.update()

                # update bullets
                self._update_bullets()

                # update alien position
                self._update_aliens()

            # redraw the screen during each pass through the loop
            self._update_screen()

            # update screen 60 times per second
            self.clock.tick(60)


if __name__ == '__main__':
    # make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()
