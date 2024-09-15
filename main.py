# Space Survival Game

import pygame
import random
import os

# Constants
FPS = 60
WIDTH = 500
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        """Initialize the game, screen, clock, and load assets"""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Survival")
        self.clock = pygame.time.Clock()
        self.running = True  # Game loop control
        self.font_name = os.path.join("font.ttf")
        
        # Load images and sounds
        self.load_assets()
    
    def load_assets(self):
        """Load all game assets including images and sounds"""
        self.background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
        self.player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
        self.player_mini_img = pygame.transform.scale(self.player_img, (25, 19))
        self.player_mini_img.set_colorkey(BLACK)
        pygame.display.set_icon(self.player_mini_img)
        
        self.bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
        self.rock_imgs = [pygame.image.load(os.path.join("img", f"rock{i}.png")).convert() for i in range(7)]
        
        # Explosion animations
        self.expl_anim = {'lg': [], 'sm': [], 'player': []}
        for i in range(9):
            expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
            expl_img.set_colorkey(BLACK)
            self.expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
            self.expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
            player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
            player_expl_img.set_colorkey(BLACK)
            self.expl_anim['player'].append(player_expl_img)
        
        # Power-up images
        self.power_imgs = {
            'shield': pygame.image.load(os.path.join("img", "shield.png")).convert(),
            'gun': pygame.image.load(os.path.join("img", "gun.png")).convert()
        }

        # Load sounds
        self.shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
        self.gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
        self.shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
        self.die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
        self.expl_sounds = [
            pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
            pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
        ]
        pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
        pygame.mixer.music.set_volume(0.4)
    
    def new_game(self):
        """Start a new game, initialize all game objects"""
        self.all_sprites = pygame.sprite.Group()
        self.rocks = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powers = pygame.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        for i in range(8):
            self.new_rock()

        self.score = 0

    def new_rock(self):
        """Create a new rock and add it to the game"""
        rock = Rock(self)
        self.all_sprites.add(rock)
        self.rocks.add(rock)
    
    def draw_text(self, text, size, x, y):
        """Helper function to draw text on the screen"""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        self.screen.blit(text_surface, text_rect)

    def draw_init(self):
        """Draw the initial screen before the game starts"""
        self.screen.blit(self.background_img, (0, 0))
        self.draw_text('Space Survival!', 64, WIDTH / 2, HEIGHT / 4)
        self.draw_text('← → to move, SPACE to shoot', 22, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press any key to start', 18, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True
                elif event.type == pygame.KEYDOWN:
                    waiting = False
                    return False

    def draw_health(self, hp, x, y):
        """Draw the player's health bar"""
        if hp < 0:
            hp = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 10
        fill = (hp / 100) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(self.screen, GREEN, fill_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

    def draw_lives(self, lives, img, x, y):
        """Draw the player's remaining lives"""
        for i in range(lives):
            img_rect = img.get_rect()
            img_rect.x = x + 32 * i
            img_rect.y = y
            self.screen.blit(img, img_rect)
    
    def run(self):
        """Main game loop"""
        pygame.mixer.music.play(-1)
        self.show_init = True
        while self.running:
            if self.show_init:
                close = self.draw_init()
                if close:
                    break
                self.show_init = False
                self.new_game()

            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shoot()

    def update(self):
        """Update all game objects and handle collisions"""
        self.all_sprites.update()

        # Check bullet-rock collisions
        hits = pygame.sprite.groupcollide(self.rocks, self.bullets, True, True)
        for hit in hits:
            random.choice(self.expl_sounds).play()
            self.score += hit.radius
            expl = Explosion(hit.rect.center, 'lg', self)
            self.all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Power(hit.rect.center, self)
                self.all_sprites.add(pow)
                self.powers.add(pow)
            self.new_rock()

        # Check rock-player collisions
        hits = pygame.sprite.spritecollide(self.player, self.rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            self.new_rock()
            self.player.health -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm', self)
            self.all_sprites.add(expl)
            if self.player.health <= 0:
                death_expl = Explosion(self.player.rect.center, 'player', self)
                self.all_sprites.add(death_expl)
                self.die_sound.play()
                self.player.lives -= 1
                self.player.health = 100
                self.player.hide()

        # Check player-powerup collisions
        hits = pygame.sprite.spritecollide(self.player, self.powers, True)
        for hit in hits:
            if hit.type == 'shield':
                self.player.health += 20
                if self.player.health > 100:
                    self.player.health = 100
                self.shield_sound.play()
            elif hit.type == 'gun':
                self.player.gunup()
                self.gun_sound.play()

        # If the player runs out of lives, reset the game
        if self.player.lives == 0 and not death_expl.alive():
            self.show_init = True

    def draw(self):
        """Render all game objects on the screen"""
        self.screen.fill(BLACK)
        self.screen.blit(self.background_img, (0, 0))
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 18, WIDTH / 2, 10)
        self.draw_health(self.player.health, 5, 15)
        self.draw_lives(self.player.lives, self.player_mini_img, WIDTH - 100, 15)
        pygame.display.update()

class Player(pygame.sprite.Sprite):
    """Player class for the spaceship"""
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.transform.scale(game.player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        """Update player position and status"""
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """Shoot bullets"""
        if not self.hidden:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.game)
                self.game.all_sprites.add(bullet)
                self.game.bullets.add(bullet)
                self.game.shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery, self.game)
                bullet2 = Bullet(self.rect.right, self.rect.centery, self.game)
                self.game.all_sprites.add(bullet1)
                self.game.all_sprites.add(bullet2)
                self.game.bullets.add(bullet1)
                self.game.bullets.add(bullet2)
                self.game.shoot_sound.play()

    def hide(self):
        """Temporarily hide the player after death"""
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    def gunup(self):
        """Increase gun power"""
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    """Rock class representing enemy objects"""
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image_ori = random.choice(game.rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        """Rotate the rock"""
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        """Update rock position and rotation"""
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    """Bullet class for player projectiles"""
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = game.bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        """Update bullet position"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Explosion class for showing explosion effects"""
    def __init__(self, center, size, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        self.image = game.expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        """Update explosion frames"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.expl_anim[self.size]):
                self.kill()
            else:
                self.image = self.game.expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    """Power-up class for adding bonuses (shield, gun upgrades)"""
    def __init__(self, center, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.type = random.choice(['shield', 'gun'])
        self.image = game.power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        """Update power-up position"""
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

# Start the game
game = Game()
game.run()
pygame.quit()
