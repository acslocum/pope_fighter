import pygame
from pygame import mixer
import argparse
import os

if __name__ == '__main__':
    screen = pygame.display.set_mode((800,600))
    running = True

    pygame.font.init() # Initialize the font module
    font = pygame.font.SysFont("Arial", 20) # Create a Font object

    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    directory : str = args.directory
    if not directory.endswith('/'):
        directory = directory + '/'

    extension = '.mp3'

    matching_files = []
    for filename in os.listdir(directory):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory, filename)):
            matching_files.append(filename)
    
    if len(matching_files) == 0:
        print(f'No MP3 files found in {args.directory}, exiting...')
        exit(-1)

    #print(f'MP3 files found: {matching_files}')
    mixer.init()
    pygame.init()

    sequenceID = 0
    pygame.mixer.music.load(directory + matching_files[sequenceID])
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play()
    
    font = pygame.font.SysFont('Arial', 20, bold=True, italic=False)
    
    while running:
        # check for key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sequenceID = (sequenceID + 1) % len(matching_files)
                    pygame.mixer.music.load(directory + matching_files[sequenceID])
                    pygame.mixer.music.play()

        screen.fill( (0,0,0) )
        screen_center = screen.get_rect().center
        img = font.render(matching_files[sequenceID], True, (255,255,255))
        img_rect = img.get_rect()
        img_rect.center = screen_center
        screen.blit(img, img_rect)
        pygame.display.update()
