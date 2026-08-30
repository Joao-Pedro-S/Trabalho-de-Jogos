import random # usado para as minas
# Classe base abstrata (Abstract Base Class)
from abc import ABC, abstractmethod

import pygame


# objeto herda de classe abstrata
## nunca pode ser criada, só as filhas
class Obj(ABC):

    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        # lista de sprites, chave = nome
        self.sprites = sprites

    @abstractmethod
    def draw(self, screen):
        # não fará nada como parente
        pass

    # pela natureza do jogo, nem o grid nem as células usam delta time para se alterar
    #@abstractmethod
    #def update(self, dt):
    #    pass


class Cell(Obj):
    # um tile no grid de campo minado

    def __init__(self, x, y, sprites, size, row, col):
        # definição de tamanhos e manda os atributos comuns para o parente
        super().__init__(x, y, sprites)
        self.size = size
        self.row = row
        self.col = col

        # definição de estados
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.is_exploded = False
        self.adjacent_mines = 0

    # comportamentos da célula
    def reveal(self):
        if self.is_flagged or self.is_revealed:
            return
        self.is_revealed = True
        if self.is_mine:
            self.is_exploded = True

    def toggle_flag(self):
        if self.is_revealed:
            return
        self.is_flagged = not self.is_flagged

    def current_sprite(self):
        # define qual sprite deve ser exibido
        if self.is_revealed:
            if self.is_mine:
                return self.sprites["exploded"] if self.is_exploded else self.sprites["mine"]
            if self.adjacent_mines == 0:
                return self.sprites["empty"]
            return self.sprites[f"number_{self.adjacent_mines}"]

        if self.is_flagged:
            return self.sprites["flag"]
        return self.sprites["unknown"]

    # draw
    def draw(self, screen):
        screen.blit(self.current_sprite(), (self.x, self.y))

    def draw_selection(self, screen, color):
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size), 2)


class Grid(Obj):
    # Contém as células e mantém todas as regras do jogo

    def __init__(self, x, y, sprites, grid_size, cell_size, mine_count):
        # definição de tamanhos e manda os atributos comuns para o parente
        super().__init__(x, y, sprites)
        self.rows, self.cols = grid_size
        self.cell_size = cell_size
        self.mine_count = mine_count

        # a matriz em si
        self.cells = [
            [
                Cell(
                    self.x + col * self.cell_size,
                    self.y + row * self.cell_size,
                    sprites,
                    self.cell_size,
                    row,
                    col,
                )
                for col in range(self.cols)
            ]
            for row in range(self.rows)
        ]

        # definição de estados
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.flags_used = 0
        self.revealed_count = 0

    # setup
    def _neighbors_coords(self, row, col):
        coords = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    coords.add((r, c))
        return coords

    def _count_adjacent_mines(self, row, col):
        return sum(
            1 for (r, c) in self._neighbors_coords(row, col) if self.cells[r][c].is_mine
        )

    def place_mines(self, safe_row, safe_col):
        # As minas são posicionadas apenas depois do primeiro clique,
        # também mantém um espaço aberto no começo, para que não haja
        # uma situação onde só há 1 único tile revelado no inicio do jogo
        forbidden = self._neighbors_coords(safe_row, safe_col)|{(safe_row, safe_col)}
        possible = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in forbidden
        ]
        mine_positions = random.sample(possible, min(self.mine_count, len(possible)))
        for (r, c) in mine_positions:
            self.cells[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if not self.cells[r][c].is_mine:
                    self.cells[r][c].adjacent_mines = self._count_adjacent_mines(r, c)

        self.mines_placed = True

    # comportamentos

    # usado para interação com o mouse na main
    def cell_at_pixel(self, px, py):
        if px < self.x or py < self.y:
            return None
        col = (px - self.x) // self.cell_size
        row = (py - self.y) // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[int(row)][int(col)]
        return None

    def reveal_cell(self, row, col):
        if self.game_over:
            return

        if not self.mines_placed:
            self.place_mines(row, col)

        cell = self.cells[row][col]
        if cell.is_flagged or cell.is_revealed:
            return

        cell.reveal()

        if cell.is_mine:
            self.game_over = True
            self.won = False
            self._reveal_all_mines()
            return

        self.revealed_count += 1
        if cell.adjacent_mines == 0:
            self._flood_reveal(row, col)

        self._check_win()

    # algoritmo de enchente iterativo adaptado para campo minado, não fui eu que inventei
    def _flood_reveal(self, row, col):
        stack = list(self._neighbors_coords(row, col))
        while stack:
            r, c = stack.pop()
            cell = self.cells[r][c]
            if cell.is_revealed or cell.is_flagged or cell.is_mine:
                continue
            cell.reveal()
            self.revealed_count += 1
            if cell.adjacent_mines == 0:
                stack.extend(self._neighbors_coords(r, c))

    def toggle_flag(self, row, col):
        if self.game_over:
            return
        cell = self.cells[row][col]
        if cell.is_revealed:
            return
        cell.toggle_flag()
        self.flags_used += 1 if cell.is_flagged else -1

    def _reveal_all_mines(self):
        for row in self.cells:
            for cell in row:
                if cell.is_mine:
                    cell.is_revealed = True

    def _check_win(self):
        total_safe = self.rows * self.cols - self.mine_count
        if self.revealed_count >= total_safe:
            self.game_over = True
            self.won = True

    def mines_remaining(self):
        return max(self.mine_count - self.flags_used, 0)

    # draw
    def draw(self, screen):
        for row in self.cells:
            for cell in row:
                cell.draw(screen)

