import pygame
import argparse

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
    parser.add_argument('filename')
    parser.add_argument('-c', '--columns', type=int)
    parser.add_argument('-r', '--rows', type=int)
    parser.add_argument('-n', '--num_images', type=int)
    args = parser.parse_args()
    print(args.filename, args.columns, args.rows, args.num_images)
    filename = args.filename
    sprite_layout = (args.columns, args.rows) # columns, rows - might not be complete
    num_sprites = args.num_images

    spritesheet = pygame.image.load(filename).convert_alpha()

    sprites = get_sequence(spritesheet, sprite_layout, num_sprites)
    spriteID = 0

    #sprite_size = (spritesheet.get_width() // sprite_layout[0], spritesheet.get_height() // sprite_layout[1])
    #print(f'Sprite sheet dimensions: {spritesheet.get_size()}, image dimensions: {sprite_size}')

    while running:
        # check for key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False

        screen.fill((0,0,0))
        screen.blit(sprites[spriteID], (100, 100)) # Blit the sprite at coordinates (100, 100)
        pygame.display.flip()
        clock.tick(FPS)
        # advance to next frame
        spriteID = (spriteID + 1) % len(sprites)
