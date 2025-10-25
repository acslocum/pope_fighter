import pygame
import argparse
import os

def get_sprite_from_sheet(sheet, x, y, width, height) -> pygame.Surface:
    image = pygame.Surface((width, height), pygame.SRCALPHA) # SRCALPHA for transparency
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image

def get_sequence(sheet : pygame.Surface, sheet_dim : tuple[int], num_images : int) -> list[list[pygame.Surface]]:
    sprite_sequence = []
    sprite_w = sheet.get_width() // sheet_dim[0]
    sprite_h = sheet.get_height() // sheet_dim[1]
    count = 0
    for row in range(sheet_dim[1]):
        for col in range(sheet_dim[0]):
            if count < num_images:
                img = get_sprite_from_sheet(sheet, col * sprite_w, row * sprite_h, sprite_w, sprite_h)
                sprite_sequence.append(img)
                count += 1

    print(f'Sprite size: {sprite_w} x {sprite_h}')
    return sprite_sequence

def parseDescriptionFile(filename : str) -> dict:
    with open(filename, 'r') as file:
        description = {}
        for line in file:
            if line.startswith('#'):
                pass
            else:
                fields = line.strip().split(',')
                if len(fields) == 4:
                    dimensions = {'rows' : int(fields[2]), 'columns' : int(fields[1]), 'count' : int(fields[3])}
                    description[fields[0]] = dimensions
        return description



if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    FPS = 10
    running = True

     # Extract sprites
    # spritesheet = pygame.image.load('/Users/sean/Documents/Fortress Party/Fortress Party 2025/godmodeAI/left_pope_walking_transparent.png').convert_alpha()
    # sprite_layout = (4,7) # columns, rows - might not be complete
    # num_sprites = 28
    #filename = '/Users/sean/Documents/Fortress Party/Fortress Party 2025/godmodeAI/pope1/left_pope_idle_transparent.png'
    #sprite_layout = (4,8) # columns, rows - might not be complete
    #num_sprites = 29

    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    #print(args.directory)

    desc_filename = 'descriptions.txt' # there should be one of these at the top of each character dir
    sheet_filename = 'spritesheet.png' # should be called this for all actions

    desc_file = os.path.join(args.directory, 'descriptions.txt')
    descriptions = parseDescriptionFile(desc_file)
    #print(descriptions)

    sprites = []
    for action in descriptions:
        action_dir = os.path.join(args.directory, action)
        sprite_file = os.path.join(action_dir, sheet_filename)

        sprite_layout = (descriptions[action]['columns'], descriptions[action]['rows']) # columns, rows - might not be complete
        num_sprites = descriptions[action]['count']

        spritesheet = pygame.image.load(sprite_file).convert_alpha()
        action_sprites = get_sequence(spritesheet, sprite_layout, num_sprites)

        sprites.append(action_sprites)
    
    # print(f'Number of sprite sequences: {len(sprites)}')
    # for s in sprites:
    #     print(f'. {len(s)}')
    # exit()
    sequenceID = 0
    spriteID = 0

    #sprite_size = (spritesheet.get_width() // sprite_layout[0], spritesheet.get_height() // sprite_layout[1])
    #print(f'Sprite sheet dimensions: {spritesheet.get_size()}, image dimensions: {sprite_size}')

    while running:
        # check for key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sequenceID = (sequenceID + 1) % len(sprites)
                    spriteID = 0
        screen.fill((0,0,0))
        screen.blit(sprites[sequenceID][spriteID], (100, 100)) # Blit the sprite at coordinates (100, 100)
        pygame.display.flip()
        clock.tick(FPS)
        # advance to next frame
        spriteID = (spriteID + 1) % len(sprites[sequenceID])
