import sys
from pathlib import Path
from time import sleep
import pygame  # type: ignore
# from check_sensors import get_cpu_temp
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star
from game_stats import GameStats
from button import Button
from scoreboard import ScoreBoard
import psutil
# import platform
# import subprocess

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

        # for performance monitoring
        self.cpu_usage_history = []
        self.cpu_update_interval = 30
        self.frame_count = 0

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
        self.aliens.empty()
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
        """Respond to keypress and mouse events efficiently."""
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():

            match event.type:
                case pygame.QUIT:
                    sys.exit()
                case pygame.KEYDOWN:
                    self._check_keydown_events(event, keys)
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
            self.sb.prep_score()
            self.sb.prep_level()

    def _start_game(self):
        """start the game"""
        # reset game stats
        self.stats.reset_stats()
        self.game_active = True

        self.settings.initialize_dynamic_settings()

        # Get rid of any remaining bullets and aliens
        self.bullets.empty()
        self.aliens.empty()

        # create new fleet and center
        self._create_fleet()
        self.ship.center_ship()

        self.sb.prep_score()
        self.sb.prep_level()

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
        """Respond to bullet-alien collisions. (optimized)"""
        # check for any bullets that have hit aliens.
        # if so, get rid of the bullet and the alien
        if not self.aliens:  # Skip collision checks if no aliens exist
            return

        # Get the lowest alien position to optimize bullet checks
        min_alien_top = min(alien.rect.top for alien in self.aliens)

        # Broad phase: Only check bullets that are near aliens
        bullets_to_check = [
            bullet for bullet in self.bullets
            if bullet.rect.bottom > min_alien_top
        ]

        # Perform collision check only on nearby bullets
        collisions = pygame.sprite.groupcollide(
            pygame.sprite.Group(bullets_to_check), self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            self.explosion_sound.play()

        if not self.aliens:
            # Destroy bullets and create a new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _update_screen(self):
        """Update changed parts of the screen"""
        changed_rects = []
        self.screen.fill(self.settings.bg_color)

        # update stars
        for star in self.stars:
            star.draw_star()
            changed_rects.append(star.rect)

        # update bullets
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
            changed_rects.append(bullet.rect)

        # update ship
        self.ship.blitme()
        changed_rects.append(self.ship.rect)

        # update aliens
        self.aliens.draw(self.screen)
        for alien in self.aliens:
            changed_rects.append(alien.rect)

        # update score
        self.sb.show_score()
        changed_rects.append(self.sb.score_rect)

        # update play button if game is inactive
        if not self.game_active:
            self.play_button.draw_button()
            changed_rects.append(self.play_button.rect)

        # get fps
        fps = self.clock.get_fps()

        # get cpu temp
        # cpu_temp = get_cpu_temp()

        # update cpu usage every X frames
        self.frame_count += 1
        if self.frame_count % self.cpu_update_interval == 0:
            self.cpu_usage_history.append(psutil.cpu_percent(interval=0))
            if len(self.cpu_usage_history) > 10:
                self.cpu_usage_history.pop(0)

        # average cpu usage
        average_cpu_usage = sum(self.cpu_usage_history) / \
            len(self.cpu_usage_history) if self.cpu_usage_history else 0

        # render fps and cpu usage text
        font = pygame.font.Font(None, 30)
        fps_text = font.render(
            f"FPS: {fps:.2f}", True, (255, 255, 255))
        cpu_text = font.render(
            f"CPU: {average_cpu_usage:.2f}%", True, (255, 255, 255))
        # temp_text = font.render(
        #     f"CPU Temp: {cpu_temp}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))  # Display in top-left corner
        self.screen.blit(cpu_text, (10, 40))
        # self.screen.blit(temp_text, (10, 70))
        changed_rects.append(fps_text.get_rect(topleft=(10, 10)))
        changed_rects.append(cpu_text.get_rect(topleft=(10, 40)))
        # changed_rects.append(temp_text.get_rect(topleft=(10, 70)))

        # refresh only updated areas
        pygame.display.update(changed_rects)

    def _check_keydown_events(self, event, keys):
        """Respond to keypress. (optimized)"""
        # if keys[pygame.K_RIGHT]:
        #     self.ship.moving_right = True
        # if keys[pygame.K_LEFT]:
        #     self.ship.moving_left = True
        if event.key == pygame.K_p and not self.game_active:
            self._start_game()
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
        if event.key == pygame.K_q:
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
