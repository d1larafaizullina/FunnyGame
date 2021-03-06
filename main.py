import copy
import os
import sys
from pprint import pprint

import pygame
from random import choice, sample

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 30

# ЗАСТАВКА start_screen
BACKGROUND = (41, 49, 51)
CLR_TEXT = (191, 255, 0)

# Board
EMPTY = -1
BOARD_TOP = 50
BOARD_LEFT = 50
BOARD_WIDTH = 8
BOARD_HEIGHT = 8
CELL_SIZE = 64
CLR_BORDER = (201, 192, 187)
HIGHLIGHT_COLOR = (229, 43, 80)
COUNT_JEWELS = 6
SCORE_COLOR = (153, 255, 153)
ROW_ABOVE = 'невидимый ряд'
SPEED = 25

# Jewel
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


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
    intro_text = ["JEWEL BOOM", "",
                  "Правила игры:",
                  "Соберите три и более в ряд кристалла,",
                  "выделяя их поочередно"]
    fon = pygame.transform.scale(load_image('zastavka.png'), WINDOW_SIZE)
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
                # print("1. Начинаем игру!")
                return  # начинаем игру
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    # print("0. Завершаем игру!")
                    terminate()
                else:
                    # print("2. Начинаем игру!")
                    return  # начинаем игру
        pygame.display.update()
        clock.tick()


class Jewel:

    def __init__(self, num, x, y, direct=None):
        self.num = num
        self.x = x
        self.y = y
        self.direct = direct


class Board:

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.left = BOARD_LEFT
        self.top = BOARD_TOP
        self.cell_size = CELL_SIZE
        self.jewel_images = []
        self.load_jewel_images()
        self.board = [[EMPTY] * width for _ in range(height)]
        self.score_font = pygame.font.Font(None, 42)

    def generate_board(self):
        rnd = sample(list(range(len(self.jewel_images))),
                     k=len(self.jewel_images))
        for x in range(self.width):
            for y in range(self.height):
                self.board[x][y] = choice(rnd)

    def draw_board(self, board, screen):
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, CLR_BORDER, self.border_rect(x, y), 1)
                num = board[x][y]
                if num != EMPTY:
                    screen.blit(self.jewel_images[num], self.border_rect(x, y))

    def draw_score(self, screen, score, color=SCORE_COLOR):
        score_img = self.score_font.render(str(score), 1, color)
        score_rect = score_img.get_rect()
        score_rect.bottomleft = (WINDOW_WIDTH - 120, 50)
        screen.blit(score_img, score_rect)

    def moving_jewel(self, jewel, step, screen):
        dx = 0
        dy = 0
        step *= 0.01
        if jewel.direct == RIGHT:
            dx = int(step * CELL_SIZE)
        elif jewel.direct == LEFT:
            dx = -int((step * CELL_SIZE))
        elif jewel.direct == UP:
            dy = -int(step * CELL_SIZE)
        elif jewel.direct == DOWN:
            dy = int(step * CELL_SIZE)

        x = jewel.x
        y = jewel.y
        if y == ROW_ABOVE:
            y = -1

        px = self.left + (x * CELL_SIZE)
        py = self.top + (y * CELL_SIZE)
        r = pygame.Rect((px + dx, py + dy, CELL_SIZE, CELL_SIZE))
        screen.blit(self.jewel_images[jewel.num], r)

    def animate_moving(self, board, jewels, screen, clock, score):
        # print('animate_moving')
        step = 0
        while step < 100:
            screen.fill(BACKGROUND)
            self.draw_board(board, screen)
            for jewel in jewels:
                self.moving_jewel(jewel, step, screen)
            self.draw_score(screen, score)
            pygame.display.update()
            clock.tick(FPS)
            step += SPEED

    def render(self, screen, clock, score):
        drops = self.get_drops()
        # print('drops', drops)
        while drops != [[]] * BOARD_WIDTH:

            jewel_drops = self.get_jewel_drops()
            for x in range(len(drops)):
                if len(drops[x]) != 0:
                    jewel_drops.append(Jewel(drops[x][0], x, ROW_ABOVE, DOWN))
            board_copy = self.get_board_copy(jewel_drops)
            self.animate_moving(board_copy, jewel_drops, screen, clock, score)
            self.move_jewels(jewel_drops)

            for x in range(len(drops)):
                if len(drops[x]) == 0:
                    continue
                self.board[x][0] = drops[x][0]
                del drops[x][0]

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

    # def render(self, screen):
    #     for x in range(self.width):
    #         for y in range(self.height):
    #             pygame.draw.rect(screen, CLR_BORDER,
    #                              ((self.left + x * self.cell_size,
    #                                self.top + y * self.cell_size),
    #                               (self.cell_size, self.cell_size)), 1)
    #             jew_num = self.board[x][y]
    #             if jew_num != EMPTY:
    #                 # self.draw_count(screen, (x, y))
    #                 screen.blit(self.jewel_images[jew_num],
    #                             self.border_rect(x, y))

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

    def load_jewel_images(self):
        for i in range(1, COUNT_JEWELS+1):
            jewel = load_image('jewel%s.png' % i)
            if jewel.get_size() != (CELL_SIZE, CELL_SIZE):
                jewel = pygame.transform.smoothscale(jewel,
                                                     (CELL_SIZE, CELL_SIZE))
            self.jewel_images.append(jewel)

    def get_jewel(self, board, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        else:
            return board[x][y]

    def down_jewels(self, board_copy):
        # print('Board.down_jewels')
        for x in range(self.width):
            column_jewels = []
            for y in range(self.height):
                if board_copy[x][y] != EMPTY:
                    column_jewels.append(board_copy[x][y])
            board_copy[x] = ([EMPTY] * (self.height -
                                        len(column_jewels))) + column_jewels

    def get_drops(self):
        # print('Board.get_drops')
        board_copy = copy.deepcopy(self.board)
        # pprint(board_copy)
        self.down_jewels(board_copy)
        # pprint(board_copy)
        drops = []
        for i in range(self.width):
            drops.append([])

        for x in range(self.width):
            for y in range(self.height-1, -1, -1):

                if board_copy[x][y] == EMPTY:
                    # print('xy', board_copy[x][y])
                    possibles = list(range(len(self.jewel_images)))
                    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                        neighbor = self.get_jewel(board_copy, x + dx, y + dy)
                        if neighbor is None and neighbor in possibles:
                            possibles.remove(neighbor)
                    new = choice(possibles)
                    board_copy[x][y] = new
                    drops[x].append(new)
        return drops

    def get_jewel_drops(self):
        # print('Board.get_jewel_drops')
        board_copy = copy.deepcopy(self.board)
        jewel_drops = []
        for x in range(self.width):
            for y in range(self.height - 2, -1, -1):
                if board_copy[x][y + 1] == EMPTY and board_copy[x][y] != EMPTY:
                    jewel_drops.append(Jewel(board_copy[x][y], x, y, DOWN))
                    board_copy[x][y] = EMPTY
        return jewel_drops

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

    def get_board_copy(self, jewels):
        board_copy = copy.deepcopy(self.board)
        for jewel in jewels:
            if jewel.y != ROW_ABOVE:
                board_copy[jewel.x][jewel.y] = EMPTY
        return board_copy

    def move_jewels(self, jewels):
        for jewel in jewels:
            if jewel.y != ROW_ABOVE:
                self.board[jewel.x][jewel.y] = EMPTY
                dx = 0
                dy = 0
                if jewel.direct == LEFT:
                    dx = -1
                elif jewel.direct == RIGHT:
                    dx = 1
                elif jewel.direct == DOWN:
                    dy = 1
                elif jewel.direct == UP:
                    dy = -1
                self.board[jewel.x + dx][jewel.y + dy] = jewel.num
            else:
                self.board[jewel.x][0] = jewel.num

    def swap_jewels(self, first, second):
        self.board[first.x][first.y] = second.num
        self.board[second.x][second.y] = first.num

    def highlight_cell(self, x, y, screen, ):
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, self.border_rect(x, y), 4)


class Game:

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.board = Board()
        self.score = 0
        self.clicked = None  # кортеж координат
        self.l_pos = None  # последний выделенный
        self.first_sld = None  # первый выделенный
        self.jewels = []

    def get_swapping_jewels(self, first, second):
        first_jewel = Jewel(self.board.board[first[0]][first[1]],
                            first[0], first[1])
        second_jewel = Jewel(self.board.board[second[0]][second[1]],
                             second[0], second[1])
        if first_jewel.x == second_jewel.x + 1\
                and first_jewel.y == second_jewel.y:
            first_jewel.direct = LEFT
            second_jewel.direct = RIGHT
        elif first_jewel.x == second_jewel.x - 1\
                and first_jewel.y == second_jewel.y:
            first_jewel.direct = RIGHT
            second_jewel.direct = LEFT
        elif first_jewel.x == second_jewel.x\
                and first_jewel.y == second_jewel.y + 1:
            first_jewel.direct = UP
            second_jewel.direct = DOWN
        elif first_jewel.x == second_jewel.x\
                and first_jewel.y == second_jewel.y - 1:
            first_jewel.direct = DOWN
            second_jewel.direct = UP
        else:
            return None, None
        return first_jewel, second_jewel

    def run(self):
        # self.board.render(self.screen)
        self.board.render(self.screen, self.clock, self.score)
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

            elif self.clicked and self.first_sld:
                # Два кристалла выбраны, поменять местами?
                first_sw_jew, second_sw_jew = self.get_swapping_jewels(
                    self.first_sld, self.clicked)
                if first_sw_jew is None and second_sw_jew is None:
                    self.first_sld = None
                    continue
                board_copy = self.board.get_board_copy([first_sw_jew,
                                                        second_sw_jew])
                self.board.animate_moving(board_copy,
                                          [first_sw_jew, second_sw_jew],
                                          self.screen, self.clock, self.score)
                self.board.swap_jewels(first_sw_jew, second_sw_jew)
                jews_to_del = self.board.get_drop_cell()

                if not jews_to_del:
                    # Нечего менять, возвращаем все как было
                    self.board.animate_moving(board_copy,
                                              [first_sw_jew, second_sw_jew],
                                              self.screen, self.clock,
                                              self.score)
                    self.board.swap_jewels(first_sw_jew, second_sw_jew)
                else:
                    add_score = 0
                    while jews_to_del:
                        for sets in jews_to_del:
                            add_score = (len(sets) - 3) * 3 + 3
                            for jew in sets:
                                self.board.board[jew[0]][jew[1]] = EMPTY
                        self.board.render(self.screen, self.clock, self.score)
                        jews_to_del = self.board.get_drop_cell()
                        self.score += add_score

                self.first_sld = None

            self.screen.fill(BACKGROUND)
            self.board.draw_board(self.board.board, self.screen)
            if self.first_sld is not None:
                self.board.highlight_cell(self.first_sld[0], self.first_sld[1], self.screen)
            self.board.draw_score(self.screen, self.score)
            self.clock.tick(FPS)
            pygame.display.flip()


def main():
    # print(pygame.font.get_fonts())
    pygame.init()
    pygame.display.set_caption("Jewel boom")
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
