import pygame
import random

# Fenstergröße und Frames pro Sekunde
WIDTH = 480
HEIGHT = 600
FPS = 60

# Definiere Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)

TITLE = "Doodle Jump-Klon"
FONT_NAME = 'arial'

# Spielerphysik
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20
POWERUP_DURATION = 5
NUM_PLATFORMS_FOR_ENEMIES_POWERUPS = 4

# Plattformen im Spiel
PLATFORM_LIST = [(0, HEIGHT - 40, WIDTH, 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 20),
                 (125, HEIGHT - 350, 100, 20),
                 (350, 200, 100, 20),
                 (175, 100, 50, 20)]


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font(FONT_NAME)

    def new(self):
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        # Erzeuge die Plattformen
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)

        # Erzeuge Gegner und Power-ups
        self.spawn_enemies_powerups()

        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

        # Kollision des Spielers mit den Plattformen prüfen
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0

        # Kollision des Spielers mit Power-ups prüfen
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            powerup.activate_shield(self.player)

        # Kollision des Spielers mit Gegnern prüfen
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            if self.player.shield:
                enemy.kill()  # Gegner entfernen, anstatt das Spiel zu beenden
            else:
                self.playing = False  # Das Spiel beenden

        # Schild-Timer überprüfen und Schild deaktivieren, wenn die Zeit abgelaufen ist
        if self.player.shield:
            if pygame.time.get_ticks() - self.player.shield_timer > POWERUP_DURATION * 1000:
                self.player.shield = False

        # Plattformen nach oben scrollen und neue erzeugen, wenn der Spieler nach oben gelangt
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

            # Überprüfen, ob neue Plattformen erzeugt werden müssen
            if len(self.platforms) < 6:
                self.spawn_platform()

        # Überprüfen, ob der Spieler den unteren Bildschirmrand erreicht hat
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        # Überprüfen, ob das Spiel beendet ist, wenn keine Plattformen mehr vorhanden sind
        if len(self.platforms) == 0:
            self.playing = False

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()

    def draw(self):
        self.screen.fill(LIGHTBLUE)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        if self.player.shield:
            self.player.draw_shield()
        pygame.display.flip()

    def spawn_platform(self):
        # Neue Plattform erzeugen
        width = random.randrange(50, 100)
        p = Platform(
            random.randrange(0, WIDTH - width),
            random.randrange(-75, -30),
            width,
            20
        )
        self.platforms.add(p)
        self.all_sprites.add(p)

    def spawn_enemies_powerups(self):
        # Gegner und Power-ups erzeugen, wenn ausreichend Plattformen vorhanden sind
        if len(self.platforms) >= NUM_PLATFORMS_FOR_ENEMIES_POWERUPS and not self.player.shield:
            for plat in self.platforms:
                if random.random() < 0.3:  # Erzeuge zufällig einen Gegner auf einer Plattform
                    enemy = Enemy(plat)
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                if random.random() < 0.1:  # Erzeuge zufällig ein Power-up auf einer Plattform
                    powerup = PowerUp(plat)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Pfeiltasten zum Bewegen, Leertaste zum Springen", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Drücke eine Taste, um zu spielen", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running:
            return
        self.screen.fill(LIGHTBLUE)
        self.draw_text("Game Over", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Drücke eine Taste, um weiterzuspielen", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.Surface((30, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.shield = False
        self.shield_timer = 0

    def update(self):
        # Aktualisierung der Spielerposition und -geschwindigkeit basierend auf Benutzereingaben und Physik
        self.acc = pygame.math.Vector2(0, PLAYER_GRAV)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Bildschirmränder überprüfen und den Spieler auf der gegenüberliegenden Seite erscheinen lassen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def jump(self):
        # Überprüft, ob der Spieler springen kann und ändert die vertikale Geschwindigkeit entsprechend
        self.rect.x += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 1
        if hits:
            if self.shield:
                self.vel.y = -PLAYER_JUMP
            else:
                self.vel.y = -PLAYER_JUMP

    def draw_shield(self):
        # Zeichnet das Schild um den Spieler, wenn es aktiv ist
        if self.shield:
            pygame.draw.rect(self.game.screen, WHITE, self.rect.inflate(10, 10))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, platform):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(platform.rect.left + 10, platform.rect.right - 10)
        self.rect.bottom = platform.rect.top - 5

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, platform):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield'])
        self.image = pygame.Surface((30, 15))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randrange(platform.rect.left + 10, platform.rect.right - 10)
        self.rect.bottom = platform.rect.top - 5

    def activate_shield(self, player):
        if self.type == 'shield':
            player.shield = True
            player.shield_timer = pygame.time.get_ticks()

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()


# Spiel initialisieren und den Startbildschirm anzeigen
game = Game()
game.show_start_screen()
while game.running:
    game.new()
    game.show_go_screen()

pygame.quit()
