
import pygame
from player import Player
import obstacle
from alien import Alien, AlienHorde, Extra
from util import EventHandler
import threading
from random import choice

# incialização
pygame.init()
WIDTH   =  600; HEIGHT =  700
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

events = EventHandler()

class Game:
    def __init__(self):
        #player setup
        self.player = Player((WIDTH/2, HEIGHT-60))

        #setup de vidas e recorde
        self.lives = 3
        self.live_surf = pygame.image.load("images/nave/vida.png").convert_alpha()
        self.live_position = WIDTH - self.live_surf.get_width()*2
        self.score = 0
        self.font = pygame.font.SysFont('Arial', 20)
        self.over = False

        #obstacle setup
        self.shape = obstacle.shape
        self.block_size = 8
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        for i in range(self.obstacle_amount):
            self.create_obstacle(WIDTH/self.obstacle_amount*i+23, 600)

        #alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8, x_distance = 60, y_distance = 40)
        self.horde = AlienHorde(self.aliens)
        #alien extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_counter = 0
        self.first_extra = True
        events.subscribe("tiro de jogador", self.spawn_extra)
        events.subscribe("score update", self.update_score)


    def create_obstacle(self, x_start, y_start):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size
                    y = y_start + row_index * self.block_size
                    block = obstacle.Obstacle(self.block_size,(0,255,255),x,y)
                    self.blocks.add(block)

    def alien_setup(self, rows, cols, x_distance, y_distance):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance
                y = row_index * y_distance
                if row_index == 0:
                    alien_sprite = Alien('back', (x,y), 30)
                elif row_index < 3:
                    alien_sprite = Alien('mid', (x,y), 20)
                else:
                    alien_sprite = Alien('front', (x,y), 10)
                self.aliens.add(alien_sprite)

    def spawn_extra(self, data):
        self.extra_counter += 1
        if self.first_extra == True and self.extra_counter == 23: #regra do jogo
            self.first_extra = False
            self.extra_counter = 0
            self.extra.add(Extra(choice(['right', 'left']),WIDTH))
        elif self.first_extra == False and self.extra_counter == 15:
            self.extra_counter = 0
            self.extra.add(Extra(choice(['right', 'left']), WIDTH))

    def collision_checks(self):
        # jogador
        if self.player.bullets:
            for bullet in self.player.bullets:
                #jogador x obstáculo
                if pygame.sprite.spritecollide(bullet, self.blocks, True, pygame.sprite.collide_mask):
                    bullet.kill()

                #jogador x alien
                hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, True, pygame.sprite.collide_mask)
                for alien in hit_aliens:
                    bullet.kill()
                    #acelerar e recompensar
                    events.notify("alien morto", alien)

                #jogador x extra
                hit_extra = pygame.sprite.spritecollide(bullet, self.extra, True, pygame.sprite.collide_mask)
                for extra in hit_extra:
                    bullet.kill()
                    self.update_score(extra.reward)
        # aliens
        if self.horde.bullets:
            for bullet in self.horde.bullets:
                # horda x obstáculos
                if pygame.sprite.spritecollide(bullet, self.blocks, True, pygame.sprite.collide_mask):
                    bullet.kill()
                # horda x jogador
                if pygame.sprite.collide_mask(bullet, self.player.state):
                    #print("morreu")
                    bullet.kill()
                    self.lives -= 1
                    if self.lives == 0:
                        self.over = True
                    events.notify("jogador atingido", bullet)
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True, pygame.sprite.collide_mask)
                if pygame.sprite.collide_mask(alien, self.player.state):
                    self.over = True

    def life_display(self):
        for live in range(self.lives):
            x = self.live_position + live*(self.live_surf.get_width()/2)
            screen.blit(self.live_surf, (x,10))

    def score_display(self):
        score_surf = self.font.render(f'Score: {self.score}', True, (255,255,255))
        score_rect = score_surf.get_rect(topleft = (0,0))
        screen.blit(score_surf, score_rect)

    def update_score(self, amount):
        self.score += amount

    def victory_display(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render(f'VICTORY \n SCORE: {self.score}', True, (255,255,255))
            victory_rect = victory_surf.get_rect(topleft = (WIDTH/2,HEIGHT/2))
            screen.blit(victory_surf, victory_rect)
            self.over = True

    def run(self):
        self.player.update()
        self.horde.update(WIDTH)
        self.extra.update()

        self.collision_checks()

        self.horde.aliens.draw(screen)
        self.horde.bullets.draw(screen)
        self.extra.draw(screen)
        self.player.bullets.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)

        self.score_display()
        self.life_display()
        self.victory_display()

        pass


def alien_timer():
    global timer_thread
    timer_thread = threading.Timer(0.8,alien_timer)
    events.notify("alien laser", True)
    timer_thread.daemon = True #thread irá morrer ao fim do programa
    timer_thread.start()



#inscreve esse metodo pra remoção de objetos
#EventHandler().subscribe("DestroyObj", remove_obj)



# loop principal

running = True
alien_timer()
game = Game()

while running:

    screen.fill((30, 30, 30))

    game.run()

    pygame.display.flip()
    if game.over:
        running = False
    clock.tick(60)


    