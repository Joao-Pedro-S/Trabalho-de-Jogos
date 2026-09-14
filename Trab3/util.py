import pygame

def singleton(class_):
    instances = { } 
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)	# cria se ainda não existe
        return instances[class_] # armazena para mais tarde
    return getinstance # devolve a instância unica

@singleton
class EventHandler:
    def __init__(self):
        self.observers = { }  # passa a ser um dicionário onde chave é o tipo de evento

    def subscribe(self, event_name, callback): # passa o tipo de evento também
        if event_name not in self.observers: # caso não exista ainda
            self.observers[event_name] = [ ]  # cria um novo tipo de evento para notificar
        self.observers[event_name].append(callback) # inscreve a chamada ao evento

    def notify(self, event_name, data):
        if event_name in self.observers: # checa se tem eventos desse tipo
            for o in self.observers[event_name]: # para todos os inscritos nele
                o(data) # avise que o evento ocorreu


def colored_sprite(color, size=(32, 32), circle = True):
    sprite = pygame.Surface(size)
    if circle:
        sprite.set_colorkey((0,0,0))
        pygame.draw.circle(sprite, color, (size[0]//2, size[1]//2), size[0]//2)
    else:
        sprite.fill(color)
    return sprite

def circle_collistiion (p1, r1, p2, r2):
    euc_distance = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**(1/2)
    return  euc_distance <= r1 + r2