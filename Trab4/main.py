import pygame

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
start = (340,390)

#inicialização

class Game:
    def __init__(self):
        self.tacadas = 0
        self.raio_buraco = 25
        self.bola = Bola(start)
        self.mouse = pygame.mouse.get_pos()
        self.paredes = Paredes()
        self.areia = Areia()
        self.font = pygame.font.SysFont('Arial', 20)
        self.over = False

        #setup da água
        self.triangulo = Agua((536,536), 1, 2)
        self.triangulo.rotate(-180)
        self.reta = Agua((150,150), 1, 1)
        self.reta.resize(200,200)
        self.reta.rotate(-45)
        self.quadrado = Agua((309,196), 1, 3)
        self.agua_group = pygame.sprite.Group()
        self.agua_group.add(self.reta)
        self.agua_group.add(self.triangulo)
        self.agua_group.add(self.quadrado)


    def run(self):
        self.mouse = pygame.mouse.get_pos()
        #run
        self.check_collisions()
        self.inputs()
        self.bola.update(self.paredes)
        #draws
        pygame.draw.circle(screen, (0, 0, 0), (40, 40), self.raio_buraco)
        self.areia.draw(screen)
        self.agua_group.draw(screen)
        self.bola.draw(screen)
        self.paredes.draw()
        #display
        if not self.over:
            self.display()
            pygame.draw.line(screen, (255, 165, 0), (self.bola.rect.center[0], self.bola.rect.center[1]), self.mouse)
        else:
            victory_surf = self.font.render(f'Vitória em {self.tacadas} tacadas! \nPressione ESC para sair.', True, (0, 0, 0))
            victory_rect = victory_surf.get_rect(center=(300,300))
            screen.blit(victory_surf,victory_rect)


    def display(self):
        tacadas_surf = self.font.render(f'Tacadas: {self.tacadas}', True, (0, 0, 0))
        tacadas_rect = tacadas_surf.get_rect(topleft=(500,0))
        screen.blit(tacadas_surf, tacadas_rect)

    def check_collisions(self):
        #água
        if pygame.sprite.spritecollideany(self.bola, self.agua_group, pygame.sprite.collide_mask):
            self.bola.speedy *= 0.95
            self.bola.speedx *= 0.95
            if self.bola.speedx < 0.1 and self.bola.speedy < 0.1:
                self.bola.rect.x = start[0]
                self.bola.rect.y = start[1]
                self.bola.speedx = 0
                self.bola.speedy = 0

        #buraco
        if 40+self.raio_buraco > self.bola.rect.centerx > 40-self.raio_buraco and 40 + self.raio_buraco > self.bola.rect.centery > 40 - self.raio_buraco and self.bola.speedx < 0.3 and self.bola.speedy < 0.3:
            self.bola.rect.centerx = 40
            self.bola.rect.centery = 40
            self.bola.speedx = 0
            self.bola.speedy = 0
            self.over = True

        #areia
        if pygame.sprite.collide_mask(self.bola, self.areia):
            self.bola.speedx *= 0.90
            self.bola.speedy *= 0.90





    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            elif event.type == pygame.MOUSEBUTTONUP and self.bola.speedx == self.bola.speedy == 0 and not self.over:
                self.bola.speedx = (self.mouse[0] - self.bola.rect.center[0])/15
                self.bola.speedy = (self.mouse[1] - self.bola.rect.center[1])/15
                self.tacadas += 1



class Bola:
    def __init__(self, pos):
        self.image = pygame.image.load("imagens/bola.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speedx = 0
        self.speedy = 0

    def update(self, paredes):
        self.check_bounds()
        self.rect.x += self.speedx
        if pygame.sprite.collide_mask(self, paredes):
            self.rect.x -= self.speedx
            self.speedx *= -1
        self.rect.y += self.speedy
        if pygame.sprite.collide_mask(self, paredes):
            self.rect.y -= self.speedy
            self.speedy *= -1
        self.speedx *= 0.96
        self.speedy *= 0.96
        if abs(self.speedx) < 0.1 and abs(self.speedy) < 0.1:
            self.speedx = 0
            self.speedy = 0

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
    def check_bounds(self):
        if self.rect.centerx <= 0:
            self.rect.x = 0
            self.speedx *= -1
        elif self.rect.centerx > 600:
            self.rect.x = 575 #600 - 25 (tamanho da bola)
            self.speedx *= -1
        if self.rect.centery <= 0:
            self.rect.y = 0
            self.speedy *= -1
        elif self.rect.centery > 600:
            self.rect.y = 575
            self.speedy *= -1



class Paredes(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("imagens/parede lados.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

    def draw(self):
        screen.blit(self.image, self.rect)

class Agua(pygame.sprite.Sprite):
    def __init__(self, pos, tam, tipo):
        super().__init__()

        self.tam = tam
        if tipo == 1:
            self.image = pygame.image.load("imagens/agua_reta.png")
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
        elif tipo == 2:
            self.image = pygame.image.load("imagens/agua_triangulo.png")
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
        else:
            self.image = pygame.image.load("imagens/agua_quadrado.png")
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def rotate(self, angulo):
        coords = (self.rect.x,self.rect.y)
        self.image = pygame.transform.rotate(self.image, angulo)
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.mask = pygame.mask.from_surface(self.image)

    def resize(self, width, height):
        coords = (self.rect.x,self.rect.y)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.mask = pygame.mask.from_surface(self.image)

class Areia(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("imagens/areia.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)



game = Game()
running = True

while running:
    ## desenho

    screen.fill((80, 200, 120))
    game.run()
    pygame.display.flip()
    clock.tick(60)
    pass