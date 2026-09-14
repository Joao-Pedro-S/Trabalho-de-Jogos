import pygame

from bullet import EnemyBullet
from util import EventHandler
from random import choice

events = EventHandler()

class Alien(pygame.sprite.Sprite):
    def __init__(self, type, pos, reward):
        super().__init__()
        file_path = "images/invaders/" + type + ".png"
        self.image = pygame.image.load(file_path)
        self.rect = self.image.get_rect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.reward = reward

    def update(self):
        pass

class AlienHorde:
    def __init__(self, aliens, speed=1, drop=20, speedup=1.02):
        self.aliens = aliens #recebe grupo da completo da main
        self.speed = speed
        self.drop = drop
        self.speedup = speedup
        self.direction = 1 #1 = direita | -1 = esquerda
        self.bullets = pygame.sprite.Group()
        events.subscribe("alien morto", self.on_death)
        events.subscribe("alien laser", self.shoot)

    def update(self, max_width):
        self.bullets.update()
        for alien in self.aliens:
            alien.rect.x = alien.rect.x + (self.speed * self.direction)

        hit_edge = any(
            alien.rect.right >= max_width or alien.rect.left < 0
            for alien in self.aliens
        )

        if hit_edge:
            self.direction *= -1
            for alien in self.aliens:
                alien.rect.y += self.drop

    def shoot(self, alien):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            self.bullets.add(EnemyBullet((random_alien.rect.x, random_alien.rect.y)))

    def on_death(self, alien):
        self.speed *= self.speedup
        events.notify("score update", alien.reward)

class Extra(pygame.sprite.Sprite):
    def __init__(self, side, width):
        super().__init__()
        self.image = pygame.image.load("images/invaders/extra.png")
        self.screen_width = width
        if side == "right":
            x = width + 50
            self.speed = -3
        else: # side == "left"
            x = -50
            self.speed = 3
        self.reward = 300

        self.rect = self.image.get_rect(topleft = (x, 50))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < -100:
            self.kill()
            #print("se foi")
        elif self.rect.x > self.screen_width+100:
            self.kill()
            #print("se foi")
