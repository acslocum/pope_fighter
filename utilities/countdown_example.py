import os
import pygame

pygame.init()
pygame.font.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
clock = pygame.time.Clock()

base_path = os.path.abspath('.')
print(f'Base path: {base_path}')

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_filename = 'assets/images/bg2.jpg'
bg_image = pygame.image.load(os.path.join(base_path,bg_filename))
bg_image = pygame.transform.smoothscale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

font_name = 'assets/fonts/Papyrus.ttc'
RED = (255,0,0)
interval_delay = 1000

def draw_outline_text(x, y, string, font, col, outline_col, window):
    positions = [(x-2,y-2), (x-2,y+2), (x+2,y-2), (x+2,y+2)]
    for position in positions:
        text = font.render(string, True, outline_col)
        textbox = text.get_rect()
        textbox.center = position
        window.blit(text, textbox)
    
    # blit center part
    text = font.render(string, True, col)
    textbox = text.get_rect()
    textbox.center = (x,y)
    window.blit(text, textbox)

def countdown():
    time = pygame.time.get_ticks()
    val = 3
    text = str(val)
    font = pygame.font.Font(font_name, size=100)
    print(f'Font height: {font.get_height()}')

    while True:
        screen.blit(bg_image, (0,0))
        x = int(0.5 * SCREEN_WIDTH)
        y = int(0.3 * SCREEN_HEIGHT)
        draw_outline_text(x,y,text, font, (255,255,0), (0,0,0), screen)

        if pygame.time.get_ticks() - time > interval_delay:
            val -= 1
            print(f'{val}, ({x}, {y})')
            if val > 0:
                text = str(val)
            elif val == 0:
                text = 'FIGHT!!'
            elif val < 0:
                return
            time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(FPS)

if __name__ == '__main__':
    print('Starting countdown')
    countdown()
    print('Finished countdown')

    time = pygame.time.get_ticks()
    val = 0
    text = str(val)
    font = pygame.font.Font(None, size=100)
    print(f'Font height: {font.get_height()}')

    while True:
        screen.blit(bg_image, (0,0))
        x = int(0.5 * SCREEN_WIDTH)
        y = int(0.3 * SCREEN_HEIGHT)
        draw_outline_text(x,y,text, font, (255,255,255), (0,0,128), screen)


        if pygame.time.get_ticks() - time > interval_delay:
            val += 1
            text = str(val)
            print(f'{val}, ({x}, {y})')
            time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(FPS)
