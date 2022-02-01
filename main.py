import copy
import os
import sys
import pygame
from random import choice, sample

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 30

# ЗАСТАВКА start_screen
BACKGROUND = (0, 0, 0)
CLR_TEXT = (0, 0, 0)

# Board
EMPTY = -1
TOP = 50
LEFT = 50
BOARD_WIDTH = 8
BOARD_HEIGHT = 8
CELL_SIZE = 64
CLR_BORDER = (255, 255, 255)  # BLUE
COUNT_JEWELS = 6


def load_image(name, color_key=None):
    fullname = os.path.join('DATA', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def start_screen(screen, clock):
    intro_text = ["JEWELS", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
    fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
    screen.fill(BACKGROUND)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, CLR_TEXT)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("1. Начинаем игру!")
                return  # начинаем игру
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    print("0. Завершаем игру!")
                    terminate()
                else:
                    print("2. Начинаем игру!")
                    return  # начинаем игру
        pygame.display.update()
        clock.tick()


class Board:

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.left = LEFT
        self.top = TOP
        self.cell_size = CELL_SIZE
        self.jewels = []
        self.load_jewels()
        self.board = [[EMPTY] * width for _ in range(height)]
        self.generate_board()

    def generate_board(self):
        rnd = sample(list(range(len(self.jewels))), k=len(self.jewels))
        for x in range(self.width):
            for y in range(self.height):
                self.board[x][y] = choice(rnd)
    #
    # def draw_count(self, screen, cell_coord):
    #     x, y = cell_coord
    #     font = pygame.font.Font(None, self.cell_size)
    #     text = font.render(str(self.board[y][x]), True, (0, 255, 0))
    #     text_x = (self.left + (x + 0.5) * self.cell_size -
    #               text.get_width() // 2)
    #     text_y = (self.top + (y + 0.5) * self.cell_size -
    #               text.get_height() // 2)
    #     text_w = text.get_width()
    #     text_h = text.get_height()
    #     screen.blit(text, (text_x, text_y))

    def render(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, CLR_BORDER,
                                 ((self.left + x * self.cell_size,
                                   self.top + y * self.cell_size),
                                  (self.cell_size, self.cell_size)), 1)
                jew_num = self.board[x][y]
                if jew_num != EMPTY:
                    # self.draw_count(screen, (x, y))
                    screen.blit(self.jewels[jew_num], self.border_rect(x, y))

    def border_rect(self, x, y):
        return pygame.Rect((self.left + x * self.cell_size,
                            self.top + y * self.cell_size),
                           (self.cell_size, self.cell_size))

    def check_click(self, pos):
        if pos:
            for x in range(self.width):
                for y in range(self.height):
                    if self.border_rect(x, y).collidepoint(pos[0], pos[1]):
                        return x, y
        return None

    def load_jewels(self):
        for i in range(1, COUNT_JEWELS+1):
            jewel = load_image('jewel%s.png' % i)
            if jewel.get_size() != (CELL_SIZE, CELL_SIZE):
                jewel = pygame.transform.smoothscale(jewel,
                                                     (CELL_SIZE, CELL_SIZE))
            self.jewels.append(jewel)

    def get_jewel(self, board, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        else:
            return board[x][y]

    def get_drop_cell(self):
        jewel_to_del = []
        board_copy = copy.deepcopy(self.board)
        for x in range(self.width):
            for y in range(self.height):
                # горизонтальные
                if self.get_jewel(board_copy, x, y) \
                        == self.get_jewel(board_copy, x + 1, y) \
                        == self.get_jewel(board_copy, x + 2, y) \
                        and self.get_jewel(board_copy, x, y) != EMPTY:
                    cell = self.get_jewel(board_copy, x, y)
                    offset = 0
                    ds = []
                    while cell == self.get_jewel(board_copy, x + offset, y):
                        ds.append((x + offset, y))
                        board_copy[x + offset][y] = EMPTY
                        offset += 1
                    jewel_to_del.append(ds)
                # вертикальные
                if self.get_jewel(board_copy, x, y) \
                        == self.get_jewel(board_copy, x, y + 1) \
                        == self.get_jewel(board_copy, x, y + 2) \
                        and self.get_jewel(board_copy, x, y) != EMPTY:
                    cell = self.get_jewel(board_copy, x, y)
                    offset = 0
                    ds = []
                    while cell == self.get_jewel(board_copy, x, y + offset):
                        ds.append((x, y + offset))
                        board_copy[x][y + offset] = EMPTY
                        offset += 1
                    jewel_to_del.append(ds)
        return jewel_to_del


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.board = Board()
        self.score = 0
        self.clicked = None
        self.l_pos = None  # last_pos
        self.first_sld = None  # first_selected

    def run(self):
        self.board.render(self.screen)
        while True:
            self.clicked = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT \
                        or (event.type == pygame.KEYUP and
                            event.key == pygame.K_ESCAPE):
                    terminate()
                elif event.type == pygame.MOUSEBUTTONUP:
                    # print('btnUp')
                    if event.pos == self.l_pos:
                        self.clicked = self.board.check_click(event.pos)
                    else:
                        self.first_sld = self.board.check_click(self.l_pos)
                        self.clicked = self.board.check_click(event.pos)
                        if not self.first_sld or not self.clicked:
                            self.first_sld = None
                            self.clicked = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # print('btnDn')
                    self.l_pos = event.pos
            if self.clicked and not self.first_sld:
                self.first_sld = self.clicked
                # print('first', self.first_selected)
            elif self.clicked and self.first_sld:
                # print('second', self.clicked)
                self.first_sld = None
                self.clicked = None
                m = self.board.get_drop_cell()
                print(m)
            self.board.render(self.screen)
            self.clock.tick(FPS)
            pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("FunnyGame")
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    start_screen(screen, clock)
    screen.fill(BACKGROUND)
    game = Game(screen, clock)
    game.run()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
