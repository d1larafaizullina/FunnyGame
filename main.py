import os
import sys
import pygame


WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 30
# ЗАСТАВКА start_screen
BACKGROUND = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)


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
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
    fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
    screen.fill(BACKGROUND)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, TEXT_COLOR)
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


def main():
    pygame.init()
    pygame.display.set_caption("myGame1")
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    start_screen(screen, clock)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        clock.tick(FPS)
        pygame.display.flip()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
