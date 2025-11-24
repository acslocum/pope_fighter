import math
import pygame
from pygame import mixer
from pygame import font
import cv2
import numpy as np
import os
import re
import requests
import sys
from audio_loader import GameSounds
from fighter import Fighter
import db_parser

# Helper Function for Bundled Assets
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

mixer.init()
pygame.init()

# Constants
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_WIDTH = 1778
SCREEN_HEIGHT = 1000
FPS = 60
ROUND_OVER_COOLDOWN = 3000
# variables for game debugging purposes
game_debug = False
game_debug = True

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Game Window
game_title = 'POPÉMON: ACENSIO'
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(game_title)
clock = pygame.time.Clock()

# Load Assets
#bg_image = cv2.imread(resource_path("assets/images/bg2.jpg"))
bg_image = pygame.image.load(resource_path("assets/images/bg2.jpg"))
bg_image = pygame.transform.smoothscale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
victory_img = pygame.image.load(resource_path("assets/images/victory.png")).convert_alpha()
warrior_victory_img = pygame.image.load(resource_path("assets/images/warrior.png")).convert_alpha()
wizard_victory_img = pygame.image.load(resource_path("assets/images/wizard.png")).convert_alpha()

# Fonts
#font_name = 'assets/fonts/Papyrus.ttc'
font_name = 'assets/fonts/Praetoria D.otf'
#font_name = 'assets/fonts/spqr.ttf'
menu_font = pygame.font.Font(resource_path(font_name), 50)
menu_font_title = pygame.font.Font(resource_path(font_name), 100)  # Larger font for title
count_font = pygame.font.Font(resource_path(font_name), 80)
score_font = pygame.font.Font(resource_path(font_name), 30)
frame_font = pygame.font.SysFont('Arial', 20, bold=True, italic=False)
# Music and Sounds
#pygame.mixer.music.load(resource_path("assets/audio/music.mp3"))
# pygame.mixer.music.set_volume(0.5)
# pygame.mixer.music.play(-1, 0.0, 5000)
# sword_fx = pygame.mixer.Sound(resource_path("assets/audio/sword.wav"))
# sword_fx.set_volume(0.5)
# magic_fx = pygame.mixer.Sound(resource_path("assets/audio/magic.wav"))
# magic_fx.set_volume(0.75)
game_sounds = GameSounds('assets/audio')

# declare pope IDs
popeServerBaseURL = 'http://localhost:3000/'
popeIDEndpoint = 'pope/'
popeServerURL = popeServerBaseURL + popeIDEndpoint
left_pope : db_parser.PopeData = None
right_pope: db_parser.PopeData = None
popeDB = db_parser.getPopes('assets/db/Pope-mon_stats.xlsx')

# Game Variables
score = [0, 0]  # Player Scores: [P1, P2]


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def gen_text_img(text, font, color):
    img = font.render(text, True, color)
    return img

def blur_bg(image):
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    blurred_image = cv2.GaussianBlur(image_bgr, (15, 15), 0)
    return cv2.cvtColor(blurred_image, cv2.COLOR_BGR2RGB)


def draw_bg(image, is_game_started=False):
    if not is_game_started:
        blurred_bg = blur_bg(image)
        blurred_bg = pygame.surfarray.make_surface(np.transpose(blurred_bg, (1, 0, 2)))
        blurred_bg = pygame.transform.scale(blurred_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(blurred_bg, (0, 0))
    else:
        image = pygame.surfarray.make_surface(np.transpose(image, (1, 0, 2)))
        image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(image, (0, 0))


def draw_button(text, font, text_col, button_col, x, y, width, height):
    pygame.draw.rect(screen, button_col, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    text_img = font.render(text, True, text_col)
    text_rect = text_img.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_img, text_rect)
    return pygame.Rect(x, y, width, height)

def aspect_scale(img, tgtSize):
    #Scales 'img' to fit into box bx/by.
    # This method will retain the original image's aspect ratio """
    bx = tgtSize[0]
    by = tgtSize[1]
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.smoothscale(img, (sx,sy))

def victory_screen(winner_img):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < ROUND_OVER_COOLDOWN:

        resized_victory_img = pygame.transform.scale(victory_img, (victory_img.get_width() * 2, victory_img.get_height() * 2))
        screen.blit(resized_victory_img, (SCREEN_WIDTH // 2 - resized_victory_img.get_width() // 2,
                                          SCREEN_HEIGHT // 2 - resized_victory_img.get_height() // 2 - 50))

        screen.blit(winner_img, (SCREEN_WIDTH // 2 - winner_img.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - winner_img.get_height() // 2 + 100))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def draw_gradient_text(text, font, x, y, colors):
    """
    Draws a gradient text by layering multiple text surfaces with slight offsets.
    """
    offset = 2
    for i, color in enumerate(colors):
        img = font.render(text, True, color)
        screen.blit(img, (x + i * offset, y + i * offset))


def main_menu():
    animation_start_time = pygame.time.get_ticks()
    prefix = 'A'
    suffix = 'Z'
    scanned = ''
    requiredScanLength = 3 + len(prefix) + len(suffix) # required length of keys to grab from a scan
    global left_pope
    global right_pope
    left_pope_name = None
    right_pope_name = None
    lastPopeID = None # keep track of previously scanned pope ID so it doesn't get scanned twice
    frame_file = 'assets/images/frame.png'
    frame_offset = 98 # number of pixels in x & y in original scale that image portions starts
    frame_height_percent = 0.6 # % of screen height frame's height should occupy
    shadow_offset = 5
    try:
        frame_img = pygame.image.load(frame_file).convert_alpha()
        scale_factor = SCREEN_HEIGHT * frame_height_percent / frame_img.get_height()
        scaled_size = (frame_img.get_width() * scale_factor, frame_img.get_height() * scale_factor)
        frame_img = pygame.transform.smoothscale(frame_img, scaled_size)
        frame_offset = frame_offset * scale_factor
        img_size = (scaled_size[0] - 2 * frame_offset, scaled_size[1] - 2 * frame_offset)

    except pygame.error as e:
        print(f"Error loading image: {e}")
        frame_img = None

    while True:
        #draw_bg(bg_image, is_game_started=False)
        screen.blit(bg_image, (0,0))
        if frame_img is not None:
            f1_x = SCREEN_WIDTH * 0.1
            f1_y = SCREEN_HEIGHT * 0.2
            f2_x = SCREEN_WIDTH * 0.9 - frame_img.get_width()
            screen.blit(frame_img, (f1_x, f1_y))
            screen.blit(frame_img, (f2_x, f1_y))
            vsImgShadow = gen_text_img('VS.', pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.1)), BLACK)
            vsImg = gen_text_img('VS.', pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.1)), YELLOW)
            screen.blit(vsImgShadow, ((SCREEN_WIDTH - vsImg.get_width() + shadow_offset) // 2, (SCREEN_HEIGHT - vsImg.get_height() + shadow_offset) // 2))
            screen.blit(vsImg, ((SCREEN_WIDTH - vsImg.get_width()) // 2, (SCREEN_HEIGHT - vsImg.get_height()) // 2))

        elapsed_time = (pygame.time.get_ticks() - animation_start_time) / 1000
        scale_factor = 1 + 0.05 * math.sin(elapsed_time * 2 * math.pi)  # Slight scaling
        scaled_font = pygame.font.Font(font_name, int(100 * scale_factor))

        title_text = game_title
        colors = [BLUE, GREEN, YELLOW]
        shadow_color = BLACK
        title_x = SCREEN_WIDTH // 2 - scaled_font.size(title_text)[0] // 2
        title_y = SCREEN_HEIGHT * 0.05

        draw_text(title_text, scaled_font, shadow_color, title_x + shadow_offset, title_y + shadow_offset)
        draw_gradient_text(title_text, scaled_font, title_x, title_y, colors)

        button_width = 280
        button_height = 60
        button_spacing = 30

        if left_pope is not None and right_pope is None:
            clear_button_x = SCREEN_WIDTH * 0.1 + (frame_img.get_width() - button_width) // 2
            clear_button_y = SCREEN_HEIGHT * 0.2 + frame_img.get_height() + button_spacing + button_height // 2
            clear_button = draw_button("Clear", menu_font, BLACK, YELLOW, clear_button_x, clear_button_y, button_width, button_height)

            # need to scan second pope
            pygame.draw.rect(screen, WHITE, (f2_x + frame_offset, f1_y + frame_offset, img_size[0], img_size[1]), 0)
            txt_img = gen_text_img('Scan Pope 2', menu_font, BLACK)
            txt_x = f2_x + (frame_img.get_width() - txt_img.get_width()) / 2
            txt_y = f1_y + (frame_img.get_height() - txt_img.get_height()) / 2
            screen.blit(txt_img, (txt_x, txt_y))

        elif right_pope is not None:
            clear_button_x = SCREEN_WIDTH * 0.9 - frame_img.get_width() + (frame_img.get_width() - button_width) // 2
            clear_button_y = SCREEN_HEIGHT * 0.2 + frame_img.get_height() + button_spacing + button_height // 2
            clear_button = draw_button("Clear", menu_font, BLACK, YELLOW, clear_button_x, clear_button_y, button_width, button_height)
            start_button = draw_button("START GAME", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
                                       SCREEN_HEIGHT * 0.75, button_width, button_height)
        else:
            # need to scan first pope
            pygame.draw.rect(screen, WHITE, (f1_x + frame_offset, f1_y + frame_offset, img_size[0], img_size[1]), 0)
            txt_img = gen_text_img('Scan Pope 1', menu_font, BLACK)
            txt_x = f1_x + (frame_img.get_width() - txt_img.get_width()) / 2
            txt_y = f1_y + (frame_img.get_height() - txt_img.get_height()) / 2
            screen.blit(txt_img, (txt_x, txt_y))

        if left_pope is not None and left_pope.image is not None:
            scaled_img = aspect_scale(left_pope.image, img_size)
            sx = f1_x + (frame_img.get_width() - scaled_img.get_width()) / 2
            sy = f1_y + (frame_img.get_height() - scaled_img.get_height()) / 2
            screen.blit(scaled_img, (sx,sy))
            if left_pope_name is not None:
                lpn_img = gen_text_img(left_pope_name, frame_font, BLACK)
                lpn_x = f1_x + (frame_img.get_width() - lpn_img.get_width()) // 2
                lpn_y = f1_y + frame_img.get_height() - frame_offset + (frame_offset - lpn_img.get_height()) // 2
                screen.blit(lpn_img, (lpn_x, lpn_y))
        if right_pope is not None and right_pope.image is not None:
            scaled_img = aspect_scale(right_pope.image, img_size)
            sx = f2_x + (frame_img.get_width() - scaled_img.get_width()) / 2
            sy = f1_y + (frame_img.get_height() - scaled_img.get_height()) / 2
            screen.blit(scaled_img, (sx,sy))
            if right_pope_name is not None:
                rpn_img = gen_text_img(right_pope_name, frame_font, BLACK)
                rpn_x = f2_x + (frame_img.get_width() - rpn_img.get_width()) // 2
                rpn_y = f1_y + frame_img.get_height() - frame_offset + (frame_offset - rpn_img.get_height()) // 2
                screen.blit(rpn_img, (rpn_x, rpn_y))
            
        #scores_button_y = SCREEN_HEIGHT // 2 - (button_height + button_spacing) * 0.5 + 50
        #exit_button_y = SCREEN_HEIGHT // 2 + (button_height + button_spacing) * 0.5 + 50

        # start_button = draw_button("START GAME", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
        #                            start_button_y, button_width, button_height)
        # scores_button = draw_button("SCORES", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
        #                             scores_button_y, button_width, button_height)
        # exit_button = draw_button("EXIT", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
        #                           exit_button_y, button_width, button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "START"
                # if scores_button.collidepoint(event.pos):
                #     return "SCORES"
                # if exit_button.collidepoint(event.pos):
                #     pygame.quit()
                #     exit()
                pass
            elif event.type == pygame.KEYDOWN:
                #print(len(pygame.key.name(event.key)))
                #scanned += event.unicode.upper()
                scanned += event.unicode
                #pattern = r"\d{3}" 
                if scanned.startswith('https://') and re.search(r"\d{3}", scanned) is not None:
                    print(scanned)
                    lastSlashIndex = scanned.rfind('/')
                    lastSlashIndex += 1
                    if lastSlashIndex != -1:
                        strID = scanned[lastSlashIndex:]
                        id = int(strID)
                        if lastPopeID != id and id in popeDB:
                            lastPopeID = id
                            pope = popeDB[id]
                            print(f'Scanned in pope ID: {id}, {pope.name}, querying server...')
                            response = None
                            try:
                                # Set a timeout of 0.5 seconds (500 milliseconds)
                                response = requests.get(popeServerURL + strID, timeout=0.5)
                                # print(f"Request successful with status code: {response.status_code}")
                                # print(response.content)
                                pope.updateFromJSON(response.content)
                            except requests.exceptions.Timeout:
                                print("The request timed out after 500 milliseconds.")
                                response = None
                            except requests.exceptions.RequestException as e:
                                print(f"An error occurred: {e}")
                                response = None

                            if left_pope is None:
                                left_pope = pope
                                left_pope_name = pope.name
                            elif right_pope is None:
                                right_pope = pope
                                right_pope_name = pope.name

                            # check to see if we have two popes
                            if left_pope and right_pope:
                                print(f'We\'ve got a match {left_pope.name} vs. {right_pope.name}')
                                #return "START"
                        elif lastPopeID == id:
                            print(f'Ignoring duplicate scane for {id}')
                        else:
                            print(f'Scanned in unknown pope ID: {id}')
                    else:
                        print(f'Illegal scan: {scanned}')

                    # reset for next scan
                    scanned = ''
                elif scanned.startswith('*'):
                    print(f'{scanned}')
                    if re.search(r"\d{3}", scanned) is not None:
                        strID = scanned[1:]
                        id = int(strID)
                        if id in popeDB:
                            pope = popeDB[id]
                            print(f'Scanned in pope ID: {id}, {pope.name}, loading from local DB...')
                            if left_pope is None:
                                left_pope = pope
                                left_pope_name = pope.name
                            elif right_pope is None:
                                right_pope = pope
                                right_pope_name = pope.name

                            # check to see if we have two popes
                            if left_pope and right_pope:
                                print(f'We\'ve got a match {left_pope.name} vs. {right_pope.name}')
                                #return "START"
                    
                        # reset for next scan
                        scanned = ''

        pygame.display.update()
        clock.tick(FPS)


def scores_screen():
    while True:
        #draw_bg(bg_image)
        screen.blit(bg_image, (0,0))

        scores_title = "SCORES"
        draw_text(scores_title, menu_font_title, RED, SCREEN_WIDTH // 2 - menu_font_title.size(scores_title)[0] // 2, 50)

        score_font_large = pygame.font.Font(font_name, 60)  # Increased size for scores
        p1_text = f"P1: {score[0]}"
        p2_text = f"P2: {score[1]}"
        shadow_offset = 5

        p1_text_x = SCREEN_WIDTH // 2 - score_font_large.size(p1_text)[0] // 2
        p1_text_y = SCREEN_HEIGHT // 2 - 50
        draw_text(p1_text, score_font_large, BLACK, p1_text_x + shadow_offset, p1_text_y + shadow_offset)  # Shadow
        draw_gradient_text(p1_text, score_font_large, p1_text_x, p1_text_y, [BLUE, GREEN])  # Gradient

        p2_text_x = SCREEN_WIDTH // 2 - score_font_large.size(p2_text)[0] // 2
        p2_text_y = SCREEN_HEIGHT // 2 + 50
        draw_text(p2_text, score_font_large, BLACK, p2_text_x + shadow_offset, p2_text_y + shadow_offset)  # Shadow
        draw_gradient_text(p2_text, score_font_large, p2_text_x, p2_text_y, [RED, YELLOW])  # Gradient

        return_button = draw_button("RETURN TO MAIN MENU", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - 220, 700, 500, 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(FPS)


def reset_game():
    global fighter_1, fighter_2
    # fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    # fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    fighter_1 = Fighter(1, 0.1 * SCREEN_WIDTH, 310, False, 'assets/images/pope1', game_sounds, left_pope)
    fighter_2 = Fighter(2, 0.9 * SCREEN_WIDTH, 310, True, 'assets/images/pope1', game_sounds, right_pope)
    if game_debug:
        print('Enable debug for fighters')
        fighter_1.debug = True
        fighter_2.debug = True

def draw_health_bar(health, x, y, flip = False):
    pygame.draw.rect(screen, BLACK, (x, y, 200, 20))
    x_off = 0
    if flip:
        x_off = 200 - health * 2
    if 0 < health <= 25:
        pygame.draw.rect(screen, RED, (x + x_off, y, health * 2, 20))
    elif 25 < health <= 50:
        pygame.draw.rect(screen, YELLOW, (x + x_off, y, health * 2, 20))
    elif 50 < health <= 100:
        pygame.draw.rect(screen, GREEN, (x + x_off, y, health * 2, 20))
    pygame.draw.rect(screen, WHITE, (x, y, 200, 20), 2)

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
    interval_delay = 1000
    font = pygame.font.Font(font_name, size=int(0.2*SCREEN_HEIGHT))
    # print(f'Font height: {font.get_height()}')

    while True:
        screen.blit(bg_image, (0,0))
        x = int(0.5 * SCREEN_WIDTH)
        y = int(0.3 * SCREEN_HEIGHT)
        draw_outline_text(x,y,text, font, (255,255,0), (0,0,0), screen)

        if pygame.time.get_ticks() - time > interval_delay:
            val -= 1
            #print(f'{val}, ({x}, {y})')
            if val > 0:
                text = str(val)
            elif val == 0:
                text = 'FIGHT!!'
                effect = game_sounds.getRandEffect('intro')
                effect.play()
            elif val < 0:
                return
            time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.display.update()
        clock.tick(FPS)

    # countdown_font = pygame.font.Font(font_name, 100)
    # countdown_texts = ["3", "2", "1", "FIGHT!"]
    # index = 0
    # time = pygame.time.get_ticks()
    # interval_delay = 1000
    # draw_bg(bg_image, is_game_started=False)

    # while True:
    #     draw_bg(bg_image, is_game_started=False)

    #     text = countdown_texts[index]
    #     text_img = countdown_font.render(text, True, RED)
    #     text_width = text_img.get_width()
    #     x_pos = (SCREEN_WIDTH - text_width) // 2
    #     draw_text(text, countdown_font, RED, x_pos, SCREEN_HEIGHT // 2 - 50)

    #     if pygame.time.get_ticks() - time > interval_delay:
    #         # get next text entry
    #         print(text)
    #         #print(f'bg_image: {bg_image.get_width()} x {bg_image.get_height()}')
    #         time = pygame.time.get_ticks()
    #         index += 1
    #         if index == len(countdown_texts):
    #             effect = game_sounds.getRandEffect('intro')
    #             effect.play()
    #             return
        
    #     pygame.display.update()
    #     pygame.display.flip()
    #     clock.tick(FPS)


        #pygame.display.update()

        # for text in countdown_texts:
        #     print(text)
        #     draw_bg(bg_image, is_game_started=True)

            
        #     if text == countdown_texts[-1]:
                

        #     pygame.time.delay(1000)

def game_loop():
    global score
    reset_game()
    round_over = False
    winner_img = None
    game_started = True

    baseline_ypos = 0.8 # % down the screen for the line players stand on

    countdown()

    while True:
        #draw_bg(bg_image, is_game_started=game_started)
        screen.blit(bg_image, (0,0))

        p1_name = left_pope.name if left_pope is not None else 'P1'
        p2_name = right_pope.name if right_pope is not None else 'P2'
        if game_debug:
            p1_name = 'Pope Testus I'
            p2_name = 'Pope Beta IV'

        #draw_text(f"P1: {score[0]}", score_font, WHITE, 20, 20)
        #draw_text(f"P2: {score[1]}", score_font, WHITE, SCREEN_WIDTH - 220, 20)
        draw_text(f"{p1_name}", score_font, WHITE, 20, 20)
        draw_text(f"{p2_name}", score_font, WHITE, SCREEN_WIDTH - 220, 20)
        fighter_1.draw_health_bar(screen, pygame.Rect(20,50,200,20),False)
        fighter_2.draw_health_bar(screen, pygame.Rect(SCREEN_WIDTH-220,50,200,20), True)

        exit_button = draw_button("MaiN MeNu", menu_font, BLACK, YELLOW, SCREEN_WIDTH // 2 - 150, 20, 300, 50)

        if not round_over:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2, round_over)
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1, round_over)

            fighter_1.update()
            fighter_2.update()

            if not fighter_1.alive:
                score[1] += 1
                round_over = True
                winner_img = wizard_victory_img
            elif not fighter_2.alive:
                score[0] += 1
                round_over = True
                winner_img = warrior_victory_img
        else:
            victory_screen(winner_img)
            return

        fighter_1.draw(screen)
        fighter_2.draw(screen)

        if game_debug:
            pygame.draw.line(screen, (255,255,0), (0, SCREEN_HEIGHT * baseline_ypos), (SCREEN_WIDTH, SCREEN_HEIGHT * baseline_ypos), width=3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.collidepoint(event.pos):
                    return

        pygame.display.update()
        clock.tick(FPS)


while True:
    if game_debug:
        game_loop()
    else:
        menu_selection = main_menu()

        if menu_selection == "START":
            game_loop()
        elif menu_selection == "SCORES":
            scores_screen()
