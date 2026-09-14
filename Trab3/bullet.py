import pygame
from abc import ABC, abstractmethod
from util import EventHandler

events = EventHandler()

class Bullet (ABC):

    #def __init__(self):
    #    super().__init__()

    @abstractmethod
    def update(self):
        pass


    def destroy(self): # pede para deletar
        if self.rect.y < -50 or self.rect.y > 750:
            #print("sumiu")
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

class PlayerBullet (Bullet, pygame.sprite.Sprite):
    # exemplo, façam algo mais rebuscado

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("images/tiro/tiro_jogador.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y -= 6
        self.destroy()

    #def draw(self, screen):
    #    screen.blit(self.image, self.rect.center)

class EnemyBullet(Bullet, pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("images/tiro/tiro_alien.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += 6
        self.destroy()

