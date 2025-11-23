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

    return sprite_sequence

def parseDescriptionFile(filename : str) -> dict:
    with open(filename, 'r') as file:
        description = {}
        for line in file:
            if line.startswith('#'):
                pass
            else:
                fields = line.strip().split(',')
                if len(fields) == 7:
                    dimensions = {'action' : fields[0], 'rows' : int(fields[2]), 'columns' : int(fields[1]), 'count' : int(fields[3]), 'x_off' : int(fields[4]), 'y_off' : int(fields[5]), 'scale' : float(fields[6])}
                elif len(fields) == 6:
                    dimensions = {'action' : fields[0], 'rows' : int(fields[2]), 'columns' : int(fields[1]), 'count' : int(fields[3]), 'x_off' : int(fields[4]), 'y_off' : int(fields[5])}
                elif len(fields) == 5:
                    dimensions = {'action' : fields[0], 'rows' : int(fields[2]), 'columns' : int(fields[1]), 'count' : int(fields[3]), 'y_off' : int(fields[4])}
                elif len(fields) == 4:
                    dimensions = {'action' : fields[0], 'rows' : int(fields[2]), 'columns' : int(fields[1]), 'count' : int(fields[3]), 'y_off' : 0}
                
                description[fields[0]] = dimensions
        return description



if __name__ == "__main__":
    pygame.init()
    pygame.key.set_repeat(50,50)
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    FPS = 10
    running = True

    pygame.font.init() # Initialize the font module
    font = pygame.font.SysFont("Arial", 20) # Create a Font object

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
    loaded_offs = []
    scales = []
    actions : list[str] = []
    for action in descriptions:
        actions.append(action)
        action_dir = os.path.join(args.directory, action)
        sprite_file = os.path.join(action_dir, sheet_filename)

        sprite_layout = (descriptions[action]['columns'], descriptions[action]['rows']) # columns, rows - might not be complete
        num_sprites = descriptions[action]['count']
        loaded_offs.append( (descriptions[action]['x_off'], descriptions[action]['y_off']) )
        scales.append(descriptions[action]['scale'])

        spritesheet = pygame.image.load(sprite_file).convert_alpha()
        action_sprites = get_sequence(spritesheet, sprite_layout, num_sprites)

        sprites.append(action_sprites)
    
    # print(f'Number of sprite sequences: {len(sprites)}')
    # for s in sprites:
    #     print(f'. {len(s)}')
    # exit()
    sequenceID = 0
    spriteID = 0
    #y_offsets = [0] * len(sprites) 

    #sprite_size = (spritesheet.get_width() // sprite_layout[0], spritesheet.get_height() // sprite_layout[1])
    #print(f'Sprite sheet dimensions: {spritesheet.get_size()}, image dimensions: {sprite_size}')

    spaceReleased = True
    while running:
        # check for key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and spaceReleased:
                    sequenceID = (sequenceID + 1) % len(sprites)
                    spriteID = 0
                    spaceReleased = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                spaceReleased = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                loaded_offs[sequenceID] = (loaded_offs[sequenceID][0], loaded_offs[sequenceID][1] - 1)
            if keys[pygame.K_DOWN]:
                loaded_offs[sequenceID] = (loaded_offs[sequenceID][0], loaded_offs[sequenceID][1] + 1)
            if keys[pygame.K_LEFT]:
                loaded_offs[sequenceID] = (loaded_offs[sequenceID][0] - 1, loaded_offs[sequenceID][1])
            if keys[pygame.K_RIGHT]:
                loaded_offs[sequenceID] = (loaded_offs[sequenceID][0] + 1, loaded_offs[sequenceID][1])
            if keys[pygame.K_EQUALS]:
                scales[sequenceID] = scales[sequenceID] + 0.01
            if keys[pygame.K_MINUS]:
                scales[sequenceID] = scales[sequenceID] - 0.01
        
        screen.fill((0,0,0))
        x = 100
        y = 100
        width = 240
        height = 480
        img = sprites[sequenceID][spriteID]
        scale = scales[sequenceID]
        scaledImg = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
        screen.blit(scaledImg, (x - loaded_offs[sequenceID][0], y - loaded_offs[sequenceID][1])) # Blit the sprite at coordinates (100, 100)
        player_rect = pygame.Rect((x, y, width, height))
        pygame.draw.rect(screen, (255,0,0), player_rect, width = 1)

        pygame.draw.line(screen, (255,0,0), (0, y + height), (799, y + height), 5) 

        offsetsText = str(loaded_offs[sequenceID])
        scaleText = str(scales[sequenceID])
        text_surface = font.render(actions[sequenceID] + ' ' + offsetsText + ' ' + scaleText, True, (255, 255, 255)) # White text
        screen.blit(text_surface, ((800 - text_surface.get_width()) // 2, 40))

        pygame.display.flip()
        clock.tick(FPS)
        # advance to next frame
        spriteID = (spriteID + 1) % len(sprites[sequenceID])

    i = 0
    for action in descriptions:
        print(f'{action}: {loaded_offs[i]}, {scales[i]}')
        i += 1
