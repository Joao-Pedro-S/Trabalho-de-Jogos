import pygame
from bullet import PlayerBullet
from abc import ABC, abstractmethod
from util import EventHandler

events = EventHandler()

class Player(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()

        self.x = pos[0]
        self.y = pos[1]
        self.ready = True
        self.bullet_time = 0
        self.bullet_cooldown = 600
        self.state = NormalState(self)
        self.bullets = pygame.sprite.Group()


    def update(self):
        self.handle_input()
        self.reload()
        self.bullets.update()
        self.state.update()

    def draw(self, screen):
        self.state.draw(screen)

    def shoot(self):
        self.state.shoot()

    def reload(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.bullet_time > self.bullet_cooldown:
                self.ready = True

    def move_right(self):
        self.state.move_right()

    def move_left(self):
        self.state.move_left()

    def change_state(self, new_state):
        self.state.delete()
        self.state = new_state(self)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_SPACE and self.ready:
                    self.ready = False
                    self.shoot()
                    events.notify("tiro de jogador", self.state)
                    self.bullet_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move_left()
        if keys[pygame.K_RIGHT]:
            self.move_right()


class PlayerState(ABC):




    def __init__(self, player):
        self.P = player
        self.sprite = [pygame.image.load("images/nave/nave_1.png"),
                       pygame.image.load("images/nave/nave_2.png"),
                       pygame.image.load("images/nave/nave_3.png")]
        self.rect = self.sprite[0].get_rect(midtop=(self.P.x, self.P.y))
        self.mask = pygame.mask.from_surface(self.sprite[0])
        self.frame = 0


    def draw(self, screen):
        screen.blit(self.sprite[self.frame], self.rect)

    def delete(self):
        pass  # se precisar apagar algo na mudança de estados

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def shoot(self):
        pass




class NormalState(PlayerState):

    def update(self):
        if self.frame == 2:
           self.frame = 0
        else:
            self.frame += 1

    def move_left(self):
        if self.rect.x > 0:
            self.rect.x = self.rect.x - 5

    def move_right(self):
        if self.rect.x < 540:
            self.rect.x = self.rect.x + 5

    def shoot(self):
        self.P.bullets.add(PlayerBullet(self.rect.midtop))
        #print('tiro')


