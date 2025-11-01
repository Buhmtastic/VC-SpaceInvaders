import pygame

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.image = pygame.Surface((50, 30))
        self.image.fill((50, 205, 50)) # Lime Green
        self.rect = self.image.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.speed = 5
        self.lives = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def shoot(self, bullets):
        if not bullets:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets.add(bullet)

    def lose_life(self):
        self.lives -= 1
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

# --- Alien Class ---
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((255, 0, 0)) # Red
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Bunker Class ---
class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 40))
        self.image.fill((0, 255, 0)) # Green
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 10

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            # Change color to show damage
            self.image.fill((0, 255 - (10 - self.health) * 25, 0))

# --- UFO Class ---
class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 25))
        self.image.fill((255, 0, 255)) # Magenta
        self.rect = self.image.get_rect(center=(-30, 30))
        self.speed = 3

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 255, 0)) # Yellow
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -8

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# --- Alien Bullet Class ---
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 105, 180)) # Hot Pink
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
