import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VC-SpaceInvaders")
        self.clock = pygame.time.Clock()
        self.player = Player(self.screen)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.alien_direction = 1  # 1 for right, -1 for left
        self.alien_move_down = 0
        self.alien_fire_timer = 0
        self.font = pygame.font.Font(None, 36)
        self.bunkers = pygame.sprite.Group()
        self.ufo = pygame.sprite.GroupSingle()
        self.ufo_spawn_timer = 0
        self.score = 0
        self.wave_number = 1
        self.highscore = self.load_highscore()
        self._create_alien_grid()
        self._create_bunkers()

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except (IOError, ValueError):
            return 0

    def save_highscore(self):
        if self.score > self.highscore:
            with open("highscore.txt", "w") as f:
                f.write(str(self.score))

    def _create_alien_grid(self):
        self.aliens.empty()
        for row in range(5):
            for col in range(11):
                alien = Alien(col * 60 + 60, row * 40 + 50)
                self.aliens.add(alien)

    def _create_bunkers(self):
        self.bunkers.empty()
        for i in range(4):
            bunker = Bunker(100 + i * 200, SCREEN_HEIGHT - 150)
            self.bunkers.add(bunker)

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        self.save_highscore()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handles user input and events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE:
                    self.player.shoot(self.bullets)

    def update(self):
        """Updates game state"""
        self.player.update()
        self.bullets.update()
        self.alien_bullets.update()
        self.ufo.update()
        self._update_aliens()
        self._check_collisions()
        self._spawn_ufo()

    def _spawn_ufo(self):
        import random
        self.ufo_spawn_timer += self.clock.get_time()
        if self.ufo_spawn_timer > 10000 and not self.ufo.sprite: # Spawn every 10 seconds if no ufo
            self.ufo.add(UFO())
            self.ufo_spawn_timer = 0

    def _update_aliens(self):
        import random
        # Alien firing
        self.alien_fire_timer += self.clock.get_time()
        if self.alien_fire_timer > 1000: # Fire every 1000ms (1 second)
            if self.aliens.sprites():
                random_alien = random.choice(self.aliens.sprites())
                alien_bullet = AlienBullet(random_alien.rect.centerx, random_alien.rect.bottom)
                self.alien_bullets.add(alien_bullet)
            self.alien_fire_timer = 0

        move_down = False
        for alien in self.aliens.sprites():
            if (self.alien_direction == 1 and alien.rect.right >= SCREEN_WIDTH) or \
               (self.alien_direction == -1 and alien.rect.left <= 0):
                self.alien_direction *= -1
                move_down = True
                break

        # Calculate speed based on number of aliens and wave number
        speed_multiplier = 1 + (55 - len(self.aliens)) * 0.05
        wave_speed_bonus = self.wave_number * 0.5
        alien_speed = (wave_speed_bonus + speed_multiplier) * self.alien_direction

        for alien in self.aliens.sprites():
            alien.rect.x += alien_speed
            if move_down:
                alien.rect.y += 10 # Move down amount

            # Check for game over
            if alien.rect.bottom >= SCREEN_HEIGHT:
                self.running = False

    def _check_collisions(self):
        # Bullets hitting aliens
        if pygame.sprite.groupcollide(self.bullets, self.aliens, True, True):
            self.score += 10

        # Check for wave clear
        if not self.aliens:
            self.wave_number += 1
            self._create_alien_grid()
            self._create_bunkers() # Also reset bunkers

        # Alien bullets hitting player
        if pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
            self.player.lose_life()
            if self.player.lives <= 0:
                self.running = False # Game over

        # Player bullets hitting bunkers
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.bunkers, False)
            if hits:
                bullet.kill()
                for bunker in hits:
                    bunker.take_damage()

        # Alien bullets hitting bunkers
        for bullet in self.alien_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.bunkers, False)
            if hits:
                bullet.kill()
                for bunker in hits:
                    bunker.take_damage()

        # Player bullets hitting UFO
        if pygame.sprite.groupcollide(self.bullets, self.ufo, True, True):
            self.score += 200

    def draw(self):
        """Draws everything to the screen"""
        self.screen.fill(BLACK)
        self.player.draw()
        self.bullets.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.aliens.draw(self.screen)
        self.bunkers.draw(self.screen)
        self.ufo.draw(self.screen)
        self._draw_ui()
        pygame.display.flip()

    def _draw_ui(self):
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))
        wave_text = self.font.render(f"Wave: {self.wave_number}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 10))
        highscore_text = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
        self.screen.blit(highscore_text, (SCREEN_WIDTH - highscore_text.get_width() - 10, 40))

# --- Entry Point ---
if __name__ == "__main__":
    game = Game()
    game.run()
