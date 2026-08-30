import os

import pygame
from grid import Grid

pygame.init()
pygame.font.init()

# config
GRID_ROWS = 16
GRID_COLS = 16
MINE_COUNT = 40
CELL_SIZE = 24

GRID_X = 20
GRID_Y = 70

SIDEBAR_X = GRID_X + GRID_COLS * CELL_SIZE + 30
SIDEBAR_WIDTH = 220

WIDTH = SIDEBAR_X + SIDEBAR_WIDTH + 20
HEIGHT = GRID_Y + GRID_ROWS * CELL_SIZE + 60

BG_COLOR = (30, 30, 30)
PANEL_COLOR = (45, 45, 45)
TEXT_COLOR = (230, 230, 230)
DIM_TEXT_COLOR = (150, 150, 150)
WIN_COLOR = (110, 220, 110)
LOSE_COLOR = (220, 90, 90)
KEYBOARD_CURSOR_COLOR = (255, 215, 0)
MOUSE_HOVER_COLOR = (120, 170, 255)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Campo Minado")

font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 20)
big_font = pygame.font.Font(None, 40)


# assets
def load_sprites(): #coloca todos os sprites em um dict e retorna
    def load(name):
        image = pygame.image.load(os.path.join("images", name)).convert_alpha()
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

    sprites = {
        "unknown": load("TileUnknown.png"),
        "empty": load("TileEmpty.png"),
        "flag": load("TileFlag.png"),
        "mine": load("TileMine.png"),
        "exploded": load("TileExploded.png"),
    }
    for n in range(1, 9):
        sprites[f"number_{n}"] = load(f"Tile{n}.png")
    return sprites


sprites = load_sprites()


# game state
def make_grid():
    return Grid(GRID_X, GRID_Y, sprites, (GRID_ROWS, GRID_COLS), CELL_SIZE, MINE_COUNT)


objects = []
grid = make_grid()
objects.append(grid)

cursor_row, cursor_col = GRID_ROWS // 2, GRID_COLS // 2

# marcadores de ticks para que o timer funcione apenas depois de o jogo começar
# e até o jogo terminar, ao invés de contar desde que o pygame.init() foi chamado
start_ticks = None # usado para marcar quando o timer iniciou
end_ticks = None # usado para congelar o timer no final


def reset_game(): #quebra os contadores, recria o grid e centraliza o cursor (do teclado)
    global grid, objects, start_ticks, end_ticks, cursor_row, cursor_col
    grid = make_grid()
    objects = [grid]
    start_ticks = None
    end_ticks = None
    cursor_row, cursor_col = GRID_ROWS // 2, GRID_COLS // 2


def timer():
    if start_ticks is None:
        # jogo não iniciou ainda
        return 0.0
    # se end_ticks for None, o jogo não acabou ainda, portanto stop conterá um contador ao vivo
    stop = end_ticks if end_ticks is not None else pygame.time.get_ticks()
    # há um aviso de usar uma variável com tipo None aqui, mas o start_ticks nunca chegará aqui como None
    return (stop - start_ticks) / 1000.0 # tempo ao vivo - tempo de inicio = tempo percorrido


def draw_text(text, font_obj, color, x, y, center=False):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)
    return rect


def draw_hud():
    mines_left = grid.mines_remaining()
    display = timer()

    draw_text(f"Minas: {mines_left:03d}", font, TEXT_COLOR, GRID_X, 15)
    draw_text(f"Tempo: {display:06.1f}s", font, TEXT_COLOR, GRID_X + 160, 15)

    if grid.game_over:
        status = "Você venceu!" if grid.won else "Fim de jogo!"
        color = WIN_COLOR if grid.won else LOSE_COLOR
        draw_text(status, big_font, color, GRID_X, 40)
    else:
        draw_text("Boa sorte!", font, DIM_TEXT_COLOR, GRID_X, 42)


def draw_sidebar():
    panel_rect = pygame.Rect(SIDEBAR_X, GRID_Y, SIDEBAR_WIDTH, GRID_ROWS * CELL_SIZE)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=6)

    instructions = [
        "Controles",
        "Mouse:",
        " Botão Esquero - Revelar",
        " Botão Direito - Bandeira",
        "Teclado:",
        " WASD - Mover cursor",
        " Enter/Espaço - Revelar",
        " F - Bandeira",
        " R - Reiniciar",
        " Esc - Sair",
    ]
    base_y = GRID_Y + 20
    for i, line in enumerate(instructions):
        color = TEXT_COLOR if i == 0 else DIM_TEXT_COLOR
        draw_text(line, small_font, color, SIDEBAR_X + 15, base_y + i * 20)

def handle_reveal(row, col):
    global start_ticks
    was_game_over = grid.game_over
    if not was_game_over and start_ticks is None: # inicia o contador do timer caso seja o começo do jogo
        start_ticks = pygame.time.get_ticks()
    grid.reveal_cell(row, col)


def keyboard_cursor():
    global cursor_row, cursor_col
    cursor_row = max(0, min(GRID_ROWS - 1, cursor_row))
    cursor_col = max(0, min(GRID_COLS - 1, cursor_col))


# main loop
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) #cap de 60 atualizações por segundo

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # uso do mouse é obrigatório
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            clicked_cell = grid.cell_at_pixel(mx, my)
            if clicked_cell is not None:
                if event.button == 1:  # left button -> reveal
                    handle_reveal(clicked_cell.row, clicked_cell.col)
                elif event.button == 3:  # right button -> flag
                    grid.toggle_flag(clicked_cell.row, clicked_cell.col)

        # uso do teclado para controle é obrigatório
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_w:
                cursor_row -= 1
                keyboard_cursor()
            elif event.key == pygame.K_s:
                cursor_row += 1
                keyboard_cursor()
            elif event.key == pygame.K_a:
                cursor_col -= 1
                keyboard_cursor()
            elif event.key == pygame.K_d:
                cursor_col += 1
                keyboard_cursor()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                handle_reveal(cursor_row, cursor_col)
            elif event.key == pygame.K_f:
                grid.toggle_flag(cursor_row, cursor_col)

    # Congela o timer
    if grid.game_over and end_ticks is None:
        end_ticks = pygame.time.get_ticks()

    # desenha
    screen.fill(BG_COLOR)

    for obj in objects:
        obj.draw(screen)

    # highlight do teclado
    grid.cells[cursor_row][cursor_col].draw_selection(screen, KEYBOARD_CURSOR_COLOR)

    # highlight do mouse
    hover_cell = grid.cell_at_pixel(*pygame.mouse.get_pos())
    if hover_cell is not None:
        hover_cell.draw_selection(screen, MOUSE_HOVER_COLOR)

    draw_hud()
    draw_sidebar()

    pygame.display.flip()

pygame.quit()
