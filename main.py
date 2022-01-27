import os
import sys
import pygame
import random

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
COUNT_JEWELS = 2


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


class Board():

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.left = LEFT
        self.top = TOP
        self.cell_size = CELL_SIZE
        self.jewels = []
        self.load_jewels()
        self.jewels_rnd = list(range(len(self.jewels)))
        self.board = [[self.get_jewel()] * width for _ in range(height)]

    def get_jewel(self):
        return random.choice(self.jewels_rnd)

    def render(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, CLR_BORDER,
                                 ((self.left + x * self.cell_size,
                                   self.top + y * self.cell_size),
                                  (self.cell_size, self.cell_size)), 1)
                jew_num = self.board[x][y]
                if jew_num != EMPTY:
                    screen.blit(self.jewels[jew_num], self.border_rect(x, y))

    def border_rect(self, x, y):
        return pygame.Rect((self.left + x * self.cell_size,
                            self.top + y * self.cell_size),
                           (self.cell_size, self.cell_size))

    def check_click(self, pos):
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


class Game():

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.board = Board()
        self.score = 0

    def run(self):
        self.board.render(self.screen)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT \
                        or (event.type == pygame.KEYUP and
                            event.key == pygame.K_ESCAPE):
                    terminate()
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                    # self.board.check_click(event.pos)
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
