import math
import pygame
from pygame import mixer
from pygame import font
import cv2
import numpy as np
import os
import random
import re
import requests
import sys
from audio_loader import GameSounds
from fighter import Fighter
import db_parser
from PopeData import PopeData

# Helper Function for Bundled Assets
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

mixer.init()
pygame.init()
pygame.joystick.init()

# Constants
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
#SCREEN_WIDTH = 1778
#SCREEN_HEIGHT = 1000
NEXT_BUTTON_Y = SCREEN_HEIGHT * 0.8 # set a consistent height for the 'Next' button that is present on most screens
FPS = 60
ROUND_OVER_COOLDOWN = 3000
# variables for game debugging purposes
game_debug = False
# game_debug = True

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Game Window
game_title = 'POPÉMON: ACENSIO'
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(game_title)
clock = pygame.time.Clock()

# Load Assets
#bg_image = cv2.imread(resource_path("assets/images/bg2.jpg"))
bg_image = pygame.image.load(resource_path("assets/images/bg2.jpg"))
bg_image = pygame.transform.smoothscale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
victory_img = pygame.image.load(resource_path("assets/images/victory.png")).convert_alpha()

# Fonts
#font_name = 'assets/fonts/Papyrus.ttc'
font_name = 'assets/fonts/Praetoria D.otf'
#font_name = 'assets/fonts/spqr.ttf'
#font_name = 'assets/fonts/Archeologicaps.ttf'
menu_font = pygame.font.Font(resource_path(font_name), 50)
menu_font_title = pygame.font.Font(resource_path(font_name), 100)  # Larger font for title
count_font = pygame.font.Font(resource_path(font_name), 80)
score_font = pygame.font.Font(resource_path(font_name), 30)
high_scores_font = pygame.font.Font(resource_path('assets/fonts/Academy Engraved LET Fonts.ttf'), 60)
frame_font = pygame.font.SysFont('Arial', 20, bold=True, italic=False)
# Music and Sounds
game_sounds = GameSounds('assets/audio')
pope1_game_sounds = GameSounds('assets/audio/pope1')
pope2_game_sounds = GameSounds('assets/audio/pope2')

# declare pope IDs
popeServerBaseURL = 'http://localhost:8080/' # local testing
# popeServerBaseURL = 'https://yjjgz5xvun.us-east-2.awsapprunner.com/' # real deal
popeIDEndpoint = 'pope_json/'
popeServerURL = popeServerBaseURL + popeIDEndpoint
popeWinEndpoint = popeServerBaseURL + 'win/' # add 'popeid'
popeLoseEndpoint = popeServerBaseURL + 'lose/' # add 'popeid'
gameOverEndpoint = popeServerBaseURL + 'game/' # add 'winnerID/loserID'
scoreboardEndpoint = popeServerBaseURL + 'scoreboard/' # add 'winnerID/loserID'

left_pope : db_parser.PopeData = None
right_pope: db_parser.PopeData = None
left_joystick : pygame.joystick.Joystick = None
right_joystick : pygame.joystick.Joystick = None
previousMatch : list[int] = []

popeDB = db_parser.getPopes('assets/db/Pope-mon_stats.xlsx')
#print(f'pope DB size: {len(popeDB)}')
if game_debug:
    left_pope = popeDB[1]
    right_pope = popeDB[2]

# Game Variables
score = [0, 0]  # Player Scores: [P1, P2]


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def gen_text_img(text, font, color):
    img = font.render(text, True, color)
    return img

def render_outlined_text(text, font, text_color, outline_color, outline_width = 2):
    # Render the outline text
    outline_surface = font.render(text, True, outline_color)
    
    # Create a larger surface for the combined text and outline
    width = outline_surface.get_width() + 2 * outline_width
    height = outline_surface.get_height() + 2 * outline_width
    combined_surface = pygame.Surface((width, height), pygame.SRCALPHA) # SRCALPHA for transparency

    # Blit the outline multiple times
    for x_offset in range(-outline_width, outline_width + 1):
        for y_offset in range(-outline_width, outline_width + 1):
            if x_offset != 0 or y_offset != 0: # Avoid blitting directly on top of itself
                combined_surface.blit(outline_surface, (x_offset + outline_width, y_offset + outline_width))

    # Render the main text
    main_text_surface = font.render(text, True, text_color)
    
    # Blit the main text in the center
    combined_surface.blit(main_text_surface, (outline_width, outline_width))
    
    return combined_surface

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
    switch_music(None) # stop music for now, might replace with a victory screen
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

def draw_table(data : list[list[str]], wl_rows : tuple[int, int] = None) -> pygame.Surface:
    #font_size = 60
    #font = pygame.font.Font(font_name, font_size)  # Increased size for scores
    font = high_scores_font
    h_pad = 40 # pixels between columns
    v_pad = 20 # pixels between rows
    row_height = 0
    outline_width = 1

    # render all the cells first
    cell_images : list[list[pygame.Surface]] = []
    col_widths = [0] * len(data[0])
    #print(f'col_widths: {col_widths}')
    for row in range(len(data)):
        #print(f'data_row: {data_row}')
        cell_row : list[pygame.Surface] = []
        for col in range(len(data[row])):
            if wl_rows is not None and row in wl_rows:
                if row == wl_rows[0]:
                    text_surface = render_outlined_text(data[row][col], font, (44,234,26), (131,131,131), outline_width)
                elif row == wl_rows[1]:
                    text_surface = render_outlined_text(data[row][col], font, (255, 78, 36), (131,131,131), outline_width)
            else:
                text_surface = render_outlined_text(data[row][col], font, (237,220,26), (130,95,8), outline_width)
            if text_surface.get_width() > col_widths[col]:
                col_widths[col] = text_surface.get_width()
            if text_surface.get_height() > row_height:
                row_height = text_surface.get_height()
            cell_row.append(text_surface)
        cell_images.append(cell_row)
    #print(f'col_widths: {col_widths}')

    # calculate column offsets
    col_offsets = [ ]
    offset = 0
    for width in col_widths:
        col_offsets.append(offset)
        offset += width + h_pad
    #print(f'col_offsets: {col_offsets}')

    # create surface big enough to hold everything
    surface_width = (len(col_widths) - 1) * h_pad + sum(col_widths)
    surface_height = (len(data) - 1) * h_pad + len(data) * row_height
    table_surface = pygame.Surface( (surface_width, surface_height), pygame.SRCALPHA)

    # render each image
    center_cols = [0, 2, 3] # we want these columns to be centered
    for row in range(len(cell_images)):
        for col in range(len(cell_images[row])):
            x = col_offsets[col]
            if col in center_cols:
                x += (col_widths[col] - cell_images[row][col].get_width()) // 2
            y = row_height * row + v_pad * row
            table_surface.blit(cell_images[row][col], (x,y))

    return table_surface

def draw_error_msg(msg : str, timeout = 3000):
    if not isinstance(msg, str):
        print(f'draw_error_msg(): didn\'t get a str, got {type(msg)}')
        return
    
    padding : int = 20
    max_height : int  = 0
    max_width : int  = 0

    # split message on \n character, then render each line to an image
    errorMsgArray : list[str]= msg.split('\n')
    errorMsgImages : list[pygame.surface.Surface] = []
    for errMessage in errorMsgArray:
        errMsgImg = render_outlined_text(errMessage, pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.05)), (255,0,0), (255,255,255), 1)
        errorMsgImages.append(errMsgImg)
        max_width = errMsgImg.get_width() if errMsgImg.get_width() > max_width else max_width
        max_height = errMsgImg.get_height() if errMsgImg.get_height() > max_height else max_height

    # now draw background big enough to hold it all, and blit each item onto it
    total_height : int  = len(errorMsgImages) * max_height + 2 * padding
    backingSurf : pygame.surface.Surface = pygame.surface.Surface( (max_width, total_height), pygame.SRCALPHA)
    backingSurf.fill( (0,0,0,0) )
    offset : int  = padding
    for img in errorMsgImages:
        backingSurf.blit(img, ( (max_width - img.get_width()) // 2 , offset))
        offset += max_height

    # center error message on screen
    backingSurfRect = backingSurf.get_rect()
    backingSurfRect.center = screen.get_rect().center
    dim_overlay : pygame.surface.Surface = pygame.surface.Surface( (screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    dim_overlay.fill( (0,0,0,128) )
    screen.blit(dim_overlay, (0,0))
    screen.blit(backingSurf, backingSurfRect)

    # display and delay
    pygame.display.update()
    pygame.time.delay(3000)

def main_menu():
    animation_start_time = pygame.time.get_ticks()
    scanned = ''
    global left_pope
    global right_pope
    global previousMatch
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

    switch_music('assets/audio/background/popemon background music1.mp3')

    while True:
        #draw_bg(bg_image, is_game_started=False)
        screen.blit(bg_image, (0,0))
        if frame_img is not None:
            f1_x = SCREEN_WIDTH * 0.1
            f1_y = SCREEN_HEIGHT * 0.2
            f2_x = SCREEN_WIDTH * 0.9 - frame_img.get_width()
            screen.blit(frame_img, (f1_x, f1_y))
            screen.blit(frame_img, (f2_x, f1_y))
            # vsImgShadow = gen_text_img('VS.', pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.1)), BLACK)
            # vsImg = gen_text_img('VS.', pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.1)), YELLOW)
            vsImg = render_outlined_text('VS.', pygame.font.Font(font_name, int(SCREEN_HEIGHT * 0.1)), YELLOW, BLACK, 2)
            # screen.blit(vsImgShadow, ((SCREEN_WIDTH - vsImg.get_width() + shadow_offset) // 2, (SCREEN_HEIGHT - vsImg.get_height() + shadow_offset) // 2))
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
                        if id not in previousMatch and lastPopeID != id and id in popeDB:
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
                        elif id in previousMatch:
                            draw_error_msg('You just played in the previous match!\nGive someone else a chance!')
                        elif lastPopeID == id:
                            print(f'Ignoring duplicate scan for {id}')
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
                        if id in previousMatch:
                            draw_error_msg('You just played in the previous match!\nGive someone else a chance!')
                        elif id in popeDB:
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
                                previousMatch = [left_pope.id, right_pope.id]
                                #return "START"
                    
                        # reset for next scan
                        scanned = ''

        pygame.display.update()
        clock.tick(FPS)


def scores_screen(winner, loser):
    count = 10
    START_BUTTON = 9
    endpoint = f'{scoreboardEndpoint}{str(count)}/{winner}/{loser}'
    print(f'Sending end game: {endpoint}')
    response = None
    try:
        # Set a timeout of 0.5 seconds (500 milliseconds)
        response = requests.get(endpoint, timeout=0.5)
        # print(f"Request successful with status code: {response.status_code}")
        # print(f'scores_screen(): response: {response.content}')
        data = response.json()
        table_data = [ ['Rank', 'Name', 'Record'] ]# will be an array of arrays, first array is the header
        line_num = 1 # header row is line 0
        winningPope = popeDB[winner]
        losingPope = popeDB[loser]
        winner_line = None
        loser_line = None
        for key in data:
            line = [str(int(key) + 1)]
            name = data[key]['name']
            if name == winningPope.name:
                winner_line = line_num
            elif name == losingPope.name:
                loser_line = line_num
            wins = data[key]['wins']
            losses = data[key]['losses']
            line.append(str(name))
            line.append(f'{str(wins)} - {str(losses)}')
            table_data.append(line)
            line_num += 1
        #print(table_data)
        if game_debug:
            while len(table_data) < 13:
                table_data.append([str(len(table_data)), 'St. Debug', '0 - 0'])
        if winner_line is not None and loser_line is not None:
            wl_rows = (winner_line, loser_line)
        else:
            wl_rows = None
        tbl_surf = draw_table(table_data, wl_rows)
        
        while True:
            #draw_bg(bg_image)
            screen.blit(bg_image, (0,0))
            dim_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            dim_overlay.fill((0, 0, 0, 128)) 
            screen.blit(dim_overlay, (0,0))

            scores_title = "HIGH SCORES"
            scores_surf = render_outlined_text(scores_title, menu_font_title, (237,220,26), (130,95,8))
            screen.blit(scores_surf, ( SCREEN_WIDTH // 2 - menu_font_title.size(scores_title)[0] // 2, 50 ) )
            #draw_text(scores_title, menu_font_title, RED, SCREEN_WIDTH // 2 - menu_font_title.size(scores_title)[0] // 2, 50)
            screen.blit(tbl_surf, ((SCREEN_WIDTH - tbl_surf.get_width()) // 2, 0.1 * SCREEN_HEIGHT ) )

            button_width = 280
            button_height = 60
            return_button = draw_button("Next", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
                                        NEXT_BUTTON_Y, button_width, button_height)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if return_button.collidepoint(event.pos):
                        return
                    pass
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == START_BUTTON:
                        return

            pygame.display.update()
            clock.tick(FPS)
    except requests.exceptions.Timeout:
        print("scores_screen(): The request timed out after 500 milliseconds.")
        response = None
    except requests.exceptions.RequestException as e:
        print(f"scores_screen(): An error occurred: {e}")
        response = None

def reset_game():
    global fighter_1, fighter_2
    # fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    # fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    fighter_height_ratio = 0.6 # % of screen height for fighers to utilize
    fighter_1 = Fighter(1, 0.1 * SCREEN_WIDTH, 310, SCREEN_HEIGHT, False, 'assets/images/pope1', pope1_game_sounds, left_pope, left_joystick)
    fighter_2 = Fighter(2, 0.9 * SCREEN_WIDTH, 310, SCREEN_HEIGHT, True, 'assets/images/pope2', pope2_game_sounds, right_pope, right_joystick)
    if game_debug:
        print('Enable debug for fighters')
        fighter_1.debug = True
        fighter_2.debug = True

    # select background music for game
    background_choices = ['assets/audio/background/popemon background music2.mp3', 'assets/audio/background/popemon background music3.mp3']
    music_file = background_choices[random.randrange(len(background_choices))]
    switch_music(music_file, volume=0.3)


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

def switch_music(filename, fadeout = 1000, volume = 0.5):
    if pygame.mixer.music.get_busy():
        #pygame.mixer.music.stop()
        pygame.mixer.music.fadeout(fadeout)

    if filename is not None:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1) # loop forever

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

def record_result(winner, loser):
    winningPope = None
    losingPope = None
    START_BUTTON = 9
    if type(winner) == int:
        winningPope = popeDB[winner]
        winner = f'{winner:03d}'
    if type(loser) == int:
        losingPope = popeDB[loser]
        loser = f'{loser:03d}'
    
    if winningPope is None or losingPope is None:
        print(f'record_result() error {winner}, {loser}')
        return

    endpoint = f'{gameOverEndpoint}{winner}/{loser}'
    print(f'Sending end game: {endpoint}')
    response = None
    try:
        # Set a timeout of 0.5 seconds (500 milliseconds)
        response = requests.get(endpoint, timeout=0.5)
        data = response.json()
        # print(f'{len(data)}')
        for d in data:
            id : int = int(d['ID'])
            wins : int = int(d['wins'])
            losses : int = int(d['losses'])
            popeDB[id].wins = wins
            popeDB[id].losses = losses

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
            button_width = 280
            button_height = 60
            exit_button = draw_button("Next", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
                                        NEXT_BUTTON_Y, button_width, button_height)
            results_factor = 0.08
            rotation_angle = 45
            #winner_txt = gen_text_img('WINNER', pygame.font.Font(font_name, int(SCREEN_HEIGHT * results_factor)), GREEN)
            winner_txt = render_outlined_text('WINNER', pygame.font.Font(font_name, int(SCREEN_HEIGHT * results_factor)), GREEN, BLACK, 2)
            winner_txt = pygame.transform.rotate(winner_txt, rotation_angle)
            #loser_txt = gen_text_img('LOSER', pygame.font.Font(font_name, int(SCREEN_HEIGHT * results_factor)), RED)
            loser_txt = render_outlined_text('LOSER', pygame.font.Font(font_name, int(SCREEN_HEIGHT * results_factor)), RED, BLACK, 2)
            loser_txt = pygame.transform.rotate(loser_txt, rotation_angle)
            if frame_img is not None:
                f1_x = SCREEN_WIDTH * 0.1
                f1_y = SCREEN_HEIGHT * 0.2
                f2_x = SCREEN_WIDTH * 0.9 - frame_img.get_width()
                screen.blit(frame_img, (f1_x, f1_y))
                screen.blit(frame_img, (f2_x, f1_y))

            if winningPope is not None and winningPope.image is not None:
                scaled_img = aspect_scale(winningPope.image, img_size)
                sx = f1_x + (frame_img.get_width() - scaled_img.get_width()) / 2
                sy = f1_y + (frame_img.get_height() - scaled_img.get_height()) / 2
                screen.blit(scaled_img, (sx,sy))
                winner_rect = winner_txt.get_rect(center=(f1_x + frame_img.get_width() // 2, f1_y + frame_img.get_height() // 2))
                screen.blit(winner_txt, winner_rect)
                if winningPope.name is not None:
                    lpn_img = gen_text_img(winningPope.name, frame_font, BLACK)
                    lpn_x = f1_x + (frame_img.get_width() - lpn_img.get_width()) // 2
                    lpn_y = f1_y + frame_img.get_height() - frame_offset + (frame_offset - lpn_img.get_height()) // 2
                    screen.blit(lpn_img, (lpn_x, lpn_y))
            if losingPope is not None and losingPope.image is not None:
                scaled_img = aspect_scale(losingPope.image, img_size)
                sx = f2_x + (frame_img.get_width() - scaled_img.get_width()) / 2
                sy = f1_y + (frame_img.get_height() - scaled_img.get_height()) / 2
                screen.blit(scaled_img, (sx,sy))
                dim_overlay = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
                dim_overlay.fill((0, 0, 0, 128)) 
                screen.blit(dim_overlay, (sx,sy))
                loser_rect = winner_txt.get_rect(center=(f2_x + frame_img.get_width() // 2, f1_y + frame_img.get_height() // 2))
                screen.blit(loser_txt, loser_rect)
                if losingPope.name is not None:
                    rpn_img = gen_text_img(losingPope.name, frame_font, BLACK)
                    rpn_x = f2_x + (frame_img.get_width() - rpn_img.get_width()) // 2
                    rpn_y = f1_y + frame_img.get_height() - frame_offset + (frame_offset - rpn_img.get_height()) // 2
                    screen.blit(rpn_img, (rpn_x, rpn_y))
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.collidepoint(event.pos):
                        return
                    pass
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == START_BUTTON:
                        return

            pygame.display.update()
            clock.tick(FPS)
    except requests.exceptions.Timeout:
        print("record_result(): The request timed out after 500 milliseconds.")
        response = None
    except requests.exceptions.RequestException as e:
        print(f"record_result(): An error occurred: {e}")
        response = None

def configure_joysticks():
    num_joysticks = 2 # number needed to proceed
    joysticks = {}
    global left_joystick
    global right_joystick
    START_BUTTON = 9
    keyboard_only = False

    # wait for required number of joysticks to be plugged in
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                screen.fill(WHITE) 
                text = 'Skipping joystick config - keyboard only'
                text_img = menu_font.render(text, True, (0,0,0))
                textbox = text_img.get_rect()
                textbox.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                screen.blit(text_img, textbox)
                pygame.display.update()
                pygame.time.delay(2000)
                keyboard_only = True
                running = False

            # Handle joystick connection
            elif event.type == pygame.JOYDEVICEADDED:
                # Get the device index from the event
                device_index = event.device_index
                # Create a Joystick object and store it
                joystick = pygame.joystick.Joystick(device_index)
                joystick.init()
                joysticks[device_index] = joystick
                print(f"Joystick '{joystick.get_name()}' connected (Device Index: {device_index})")
                print(f'# of axes: {joystick.get_numaxes()}')
                print(f'# of buttons: {joystick.get_numbuttons()}')
                if len(joysticks) == num_joysticks:
                    running = False

            # Handle joystick disconnection
            elif event.type == pygame.JOYDEVICEREMOVED:
                # Get the device index from the event
                device_index = event.device_index
                # Remove the joystick from your active list
                if device_index in joysticks:
                    del joysticks[device_index]
                    print(f"Joystick disconnected (Device Index: {device_index})")

        # Fill the screen with a color (e.g., blue)
        screen.fill(WHITE) 

        if len(joysticks) < num_joysticks:
            if (num_joysticks - len(joysticks)) > 1:
                j_str = 'joysticks'
            else:
                j_str = 'joystick'
            text = f'Plug in {num_joysticks - len(joysticks)} {j_str}'
            text = text.upper()
            text_img = menu_font.render(text, True, (0,0,0))
            textbox = text_img.get_rect()
            textbox.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            screen.blit(text_img, textbox)

        # Update the display to show the changes
        pygame.display.flip()

    # wait for required number of joysticks to be plugged in
    running = True
    while not keyboard_only and running:
        # Fill the screen with a color (e.g., blue)
        screen.fill(WHITE) 

        if len(joysticks) < num_joysticks:
            text = 'This should never happen'
        else:
            text = 'Press the START button on left joystick'

        text = text.upper()
        text_img = menu_font.render(text, True, (0,0,0))
        textbox = text_img.get_rect()
        textbox.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        screen.blit(text_img, textbox)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == START_BUTTON:
                    print(f'Start button pressed on joystick {event.joy}')
                    left_joystick = joysticks[event.joy]
                    del joysticks[event.joy]
                    if len(joysticks) > 0:
                        right_joystick = joysticks[next(iter(joysticks))]
                    running = False
                else:
                    print(f"Joystick {event.joy}: Button {event.button} pressed")

        # Update the display to show the changes
        pygame.display.flip()

def game_loop():
    START_BUTTON = 9
    global score
    reset_game()
    round_over = False
    winner_img = None
    game_started = True
    if game_debug:
        print('In game_loop():')
        print(f'  left joystick present  : {str(left_joystick is not None)} {str(left_joystick)}')
        print(f'  right joystick present : {str(right_joystick is not None)} {str(right_joystick)}')
        curr_time = pygame.time.get_ticks()
        health_delay = 1000

    baseline_ypos = 0.8 # % down the screen for the line players stand on

    countdown()
    winnerID : int = None
    loserID : int = None
    exit_button = None

    while True:
        #draw_bg(bg_image, is_game_started=game_started)
        screen.blit(bg_image, (0,0))

        p1_name = left_pope.name if left_pope is not None else 'Pope Testus I'
        p2_name = right_pope.name if right_pope is not None else 'Pope Beta IV'

        draw_text(f"{p1_name}", score_font, WHITE, 20, 20)
        draw_text(f"{p2_name}", score_font, WHITE, SCREEN_WIDTH - 220, 20)
        fighter_1.draw_health_bar(screen, pygame.Rect(20,50,200,20),False)
        fighter_2.draw_health_bar(screen, pygame.Rect(SCREEN_WIDTH-220,50,200,20), True)

        if not round_over:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2, round_over)
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_1, round_over)

            fighter_1.update()
            fighter_2.update()

            if not fighter_1.alive:
                winner_img = left_pope.image 
                winnerID = left_pope.id
                loserID = right_pope.id
            elif not fighter_2.alive:
                winner_img = right_pope.image
                winnerID = right_pope.id
                loserID = left_pope.id
            if fighter_1.finished and fighter_2.finished:
                button_width = 280
                button_height = 60
                exit_button = draw_button("Next", menu_font, BLACK, GREEN, SCREEN_WIDTH // 2 - button_width // 2,
                                       NEXT_BUTTON_Y, button_width, button_height)

                pass
        else:
            victory_screen(winner_img)
            return

        fighter_1.draw(screen)
        fighter_2.draw(screen)

        if game_debug:
            pygame.draw.line(screen, (255,255,0), (0, SCREEN_HEIGHT * baseline_ypos), (SCREEN_WIDTH, SCREEN_HEIGHT * baseline_ypos), width=3)
            if pygame.time.get_ticks() - curr_time > health_delay:
                curr_time = pygame.time.get_ticks()
                fighter = fighter_2
                winner = fighter_1
                # if fighter.health > 0:
                #     fighter.health -= 20
                # if fighter.health <= 0:
                #     winner.victory = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if exit_button is not None:
                if event.type == pygame.MOUSEBUTTONDOWN and exit_button.collidepoint(event.pos):
                    return winnerID, loserID
                elif event.type == pygame.JOYBUTTONDOWN and event.button == START_BUTTON:
                    return winnerID, loserID

        pygame.display.update()
        clock.tick(FPS)


configure_joysticks()
while True:
    if game_debug:
        menu_selection = main_menu()
        #winner, loser = game_loop()
        #record_result(winner, loser)

        #scores_screen(winner, loser)
        scores_screen(2,1)
        exit()
    else:
        menu_selection = main_menu()

        if menu_selection == "START":
            winner, loser = game_loop()
            record_result(winner, loser)
            scores_screen(winner, loser)
