"""VC-SpaceInvaders - A Space Invaders clone inspired by the classic arcade game"""
import pygame
import sys
import random
from pathlib import Path

# --- Game Configuration Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)

# --- Gameplay Constants ---
PLAYER_SPEED = 5
BULLET_SPEED = -8
ALIEN_BULLET_SPEED = 5
UFO_SPEED = 3
ALIEN_MOVE_DOWN_AMOUNT = 10
ALIEN_FIRE_INTERVAL = 1000  # milliseconds
UFO_SPAWN_INTERVAL = 10000  # milliseconds
ANIMATION_SPEED = 500  # milliseconds

# --- Sprite Sheet Offsets ---
SPRITE_SIZE = 24
BEAM_OFFSET = 0
BOMB_OFFSET = 48
TOP_ALIEN_OFFSET = 96
MIDDLE_ALIEN_OFFSET = 144
PLAYER_OFFSET = 192

# --- Scoring ---
ALIEN_SCORE = 10
UFO_SCORE = 200

# --- File Paths ---
SPRITE_SHEET_PATH = "reference\\strip.png"
MUSIC_PATH = "sound\\VC-SpaceInvader Main Theme.mp3"
HIGHSCORE_FILE = "highscore.txt"


# --- Base Drawable Class (Inspired by reference implementation) ---
class Drawable(pygame.sprite.Sprite):
    """Base class for all drawable game objects with sprite animation support"""

    def __init__(self, sprite_sheet, offset0, offset1=None):
        """
        Initialize a drawable object with sprite animation

        Args:
            sprite_sheet: The sprite sheet surface
            offset0: X offset for first animation frame
            offset1: X offset for second animation frame (defaults to offset0 if not animated)
        """
        super().__init__()
        if offset1 is None:
            offset1 = offset0

        # Create two animation frames
        self.images = (
            pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA),
            pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        )

        # Extract frames from sprite sheet
        self.images[0].blit(sprite_sheet, (0, 0), pygame.Rect(offset0, 0, SPRITE_SIZE, SPRITE_SIZE))
        self.images[1].blit(sprite_sheet, (0, 0), pygame.Rect(offset1, 0, SPRITE_SIZE, SPRITE_SIZE))

        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.animation_timer = pygame.time.get_ticks()

    def animate(self, speed=ANIMATION_SPEED):
        """Toggle between animation frames based on time"""
        now = pygame.time.get_ticks()
        if now - self.animation_timer > speed:
            self.image_index = (self.image_index + 1) % 2
            self.image = self.images[self.image_index]
            self.animation_timer = now


# --- Player Class ---
class Player(Drawable):
    """Player ship controlled by the user"""

    def __init__(self, sprite_sheet):
        super().__init__(sprite_sheet, PLAYER_OFFSET)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = PLAYER_SPEED
        self.lives = 3

    def update(self):
        """Handle player movement based on keyboard input"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self, bullets, sprite_sheet):
        """Fire a bullet if none currently active"""
        if not bullets:
            bullet = Bullet(self.rect.centerx, self.rect.top, sprite_sheet)
            bullets.add(bullet)

    def lose_life(self):
        """Decrease life count and reset position"""
        self.lives -= 1
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

# --- Alien Class ---
class Alien(Drawable):
    """Enemy alien with row-based sprite type"""

    def __init__(self, x, y, row, sprite_sheet):
        # Determine alien type based on row
        if row == 0:
            offset = TOP_ALIEN_OFFSET
        elif 1 <= row <= 2:
            offset = MIDDLE_ALIEN_OFFSET
        else:  # Rows 3 & 4
            offset = TOP_ALIEN_OFFSET

        super().__init__(sprite_sheet, offset, offset + SPRITE_SIZE)
        self.rect.topleft = (x, y)
        self.row = row

    def update(self):
        """Animate the alien sprite"""
        self.animate()

# --- Bunker Class ---
class Bunker(pygame.sprite.Sprite):
    """Defensive bunker that protects the player"""

    MAX_HEALTH = 10
    WIDTH = 80
    HEIGHT = 40

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = self.MAX_HEALTH

    def take_damage(self):
        """Reduce health and update visual appearance"""
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Gradually darken the green color as health decreases
            green_value = 255 - (self.MAX_HEALTH - self.health) * 25
            self.image.fill((0, green_value, 0))

# --- UFO Class ---
class UFO(pygame.sprite.Sprite):
    """Bonus UFO that flies across the top of the screen"""

    WIDTH = 60
    HEIGHT = 25

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, MAGENTA, [0, 0, self.WIDTH, self.HEIGHT])
        self.rect = self.image.get_rect(center=(-30, 30))
        self.speed = UFO_SPEED

    def update(self):
        """Move UFO across the screen"""
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# --- Bullet Class ---
class Bullet(Drawable):
    """Player's bullet projectile"""

    def __init__(self, x, y, sprite_sheet):
        super().__init__(sprite_sheet, BEAM_OFFSET, BEAM_OFFSET + SPRITE_SIZE)
        self.rect.center = (x, y)
        self.speed = BULLET_SPEED

    def update(self):
        """Move bullet upward"""
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# --- Alien Bullet Class ---
class AlienBullet(Drawable):
    """Alien's bullet projectile"""

    def __init__(self, x, y, sprite_sheet):
        super().__init__(sprite_sheet, BOMB_OFFSET, BOMB_OFFSET + SPRITE_SIZE)
        self.rect.center = (x, y)
        self.speed = ALIEN_BULLET_SPEED

    def update(self):
        """Move bullet downward"""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- Main Game Class ---
class Game:
    """Main game controller that manages game state and logic"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VC-SpaceInvaders")
        self.clock = pygame.time.Clock()
        self.running = True

        # Load sprite sheet
        self.sprite_sheet = pygame.image.load(SPRITE_SHEET_PATH).convert_alpha()

        # Initialize game objects
        self.player = Player(self.sprite_sheet)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.ufo = pygame.sprite.GroupSingle()

        # Game state
        self.alien_direction = 1  # 1 for right, -1 for left
        self.alien_fire_timer = 0
        self.ufo_spawn_timer = 0
        self.score = 0
        self.wave_number = 1
        self.highscore = self.load_highscore()

        # UI
        self.font = pygame.font.Font(None, 36)

        # Initialize game elements
        self._create_alien_grid()
        self._create_bunkers()

        # Load and play music
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)

    def load_highscore(self):
        """Load high score from file, return 0 if file doesn't exist"""
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except (IOError, ValueError):
            return 0

    def save_highscore(self):
        """Save high score to file if current score is higher"""
        if self.score > self.highscore:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.score))

    def _create_alien_grid(self):
        """Create a grid of aliens"""
        self.aliens.empty()
        rows = 5
        cols = 11
        spacing_x = 40
        spacing_y = 40
        offset_x = 60
        offset_y = 50

        for row in range(rows):
            for col in range(cols):
                x = col * spacing_x + offset_x
                y = row * spacing_y + offset_y
                alien = Alien(x, y, row, self.sprite_sheet)
                self.aliens.add(alien)

    def _create_bunkers(self):
        """Create defensive bunkers"""
        self.bunkers.empty()
        bunker_count = 4
        bunker_spacing = 200
        bunker_y = SCREEN_HEIGHT - 150

        for i in range(bunker_count):
            x = 100 + i * bunker_spacing
            bunker = Bunker(x, bunker_y)
            self.bunkers.add(bunker)

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Cleanup on exit
        pygame.mixer.music.stop()
        self.save_highscore()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Handle user input and events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.player.shoot(self.bullets, self.sprite_sheet)

    def update(self):
        """Update all game entities and logic"""
        self.player.update()
        self.bullets.update()
        self.alien_bullets.update()
        self.ufo.update()
        self.aliens.update()  # Update alien animations
        self._update_alien_movement()
        self._update_alien_firing()
        self._check_collisions()
        self._spawn_ufo()

    def _spawn_ufo(self):
        """Spawn UFO periodically if none exists"""
        self.ufo_spawn_timer += self.clock.get_time()
        if self.ufo_spawn_timer > UFO_SPAWN_INTERVAL and not self.ufo.sprite:
            self.ufo.add(UFO())
            self.ufo_spawn_timer = 0

    def _update_alien_firing(self):
        """Handle alien bullet firing logic"""
        self.alien_fire_timer += self.clock.get_time()
        if self.alien_fire_timer > ALIEN_FIRE_INTERVAL:
            if self.aliens.sprites():
                random_alien = random.choice(self.aliens.sprites())
                alien_bullet = AlienBullet(
                    random_alien.rect.centerx,
                    random_alien.rect.bottom,
                    self.sprite_sheet
                )
                self.alien_bullets.add(alien_bullet)
            self.alien_fire_timer = 0

    def _update_alien_movement(self):
        """Handle alien movement and formation logic"""
        if not self.aliens:
            return

        # Check if any alien hit the edge
        move_down = False
        for alien in self.aliens.sprites():
            if (self.alien_direction == 1 and alien.rect.right >= SCREEN_WIDTH) or \
               (self.alien_direction == -1 and alien.rect.left <= 0):
                self.alien_direction *= -1
                move_down = True
                break

        # Calculate speed based on remaining aliens and wave number
        aliens_remaining = len(self.aliens)
        speed_multiplier = 1 + (55 - aliens_remaining) * 0.02
        wave_speed_bonus = self.wave_number * 0.2
        alien_speed = (wave_speed_bonus + speed_multiplier) * self.alien_direction

        # Move all aliens
        for alien in self.aliens.sprites():
            alien.rect.x += alien_speed
            if move_down:
                alien.rect.y += ALIEN_MOVE_DOWN_AMOUNT

            # Check for game over condition
            if alien.rect.bottom >= SCREEN_HEIGHT:
                self.running = False

    def _check_collisions(self):
        """Check and handle all collision detection"""
        # Player bullets hitting aliens
        if pygame.sprite.groupcollide(self.bullets, self.aliens, True, True):
            self.score += ALIEN_SCORE

        # Check for wave completion
        if not self.aliens:
            self.wave_number += 1
            self._create_alien_grid()
            self._create_bunkers()

        # Alien bullets hitting player
        if pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
            self.player.lose_life()
            if self.player.lives <= 0:
                self.running = False

        # Bullets hitting bunkers (both player and alien)
        self._check_bunker_collisions(self.bullets)
        self._check_bunker_collisions(self.alien_bullets)

        # Player bullets hitting UFO
        if pygame.sprite.groupcollide(self.bullets, self.ufo, True, True):
            self.score += UFO_SCORE

    def _check_bunker_collisions(self, bullet_group):
        """Check if bullets hit bunkers and apply damage"""
        for bullet in bullet_group:
            hits = pygame.sprite.spritecollide(bullet, self.bunkers, False)
            if hits:
                bullet.kill()
                for bunker in hits:
                    bunker.take_damage()

    def draw(self):
        """Render all game elements to the screen"""
        self.screen.fill(BLACK)

        # Draw all sprites
        self.screen.blit(self.player.image, self.player.rect)
        self.bullets.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.aliens.draw(self.screen)
        self.bunkers.draw(self.screen)
        self.ufo.draw(self.screen)

        # Draw UI elements
        self._draw_ui()

        pygame.display.flip()

    def _draw_ui(self):
        """Render UI elements (score, lives, wave, highscore)"""
        # Lives (top-left)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))

        # Score (top-right)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        # Wave (top-center)
        wave_text = self.font.render(f"Wave: {self.wave_number}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 10))

        # Highscore (below score)
        highscore_text = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
        self.screen.blit(highscore_text, (SCREEN_WIDTH - highscore_text.get_width() - 10, 40))

# --- Entry Point ---
if __name__ == "__main__":
    game = Game()
    game.run()