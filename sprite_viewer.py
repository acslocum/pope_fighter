import pygame

def get_sprite_from_sheet(sheet, x, y, width, height) -> pygame.Surface:
    image = pygame.Surface((width, height), pygame.SRCALPHA) # SRCALPHA for transparency
    image.blit(sheet, (0, 0), (x, y, width, height))
    return image

def get_sequences(sheet : pygame.Surface, size : int, step_counts : list[int]) -> list[list[pygame.Surface]]:
    sprite_sequences = []
    for row in range(len(step_counts)):
        img_sequence = []
        count = step_counts[row]
        for x in range(count):
            img_sequence.append(get_sprite_from_sheet(sheet, x * size, row * size, size, size))
        sprite_sequences.append(img_sequence)

    return sprite_sequences

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    FPS = 10
    running = True

    warrior_spritesheet = pygame.image.load('assets/images/warrior.png').convert_alpha()
    warrior_sprite_size = 162
    WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7] # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
    wizard_spritesheet = pygame.image.load('assets/images/wizard.png').convert_alpha()
    wizard_sprite_size = 250
    WIZARD_ANIMATION_STEPS = [8, 8, 2, 8, 8, 3, 7] # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death

    # Extract sprites
    warrior_sprite_sequences = get_sequences(warrior_spritesheet, warrior_sprite_size, WARRIOR_ANIMATION_STEPS)
    warrior_sequenceID = 0 # start with the first sequence, we'll use the spacebar to switch between sequences
    warrior_imageID = 0 # start with the first image in the sequence
    wizard_sprite_sequences = get_sequences(wizard_spritesheet, wizard_sprite_size, WIZARD_ANIMATION_STEPS)
    wizard_sequenceID = 0 # start with the first sequence, we'll use the spacebar to switch between sequences
    wizard_imageID = 0 # start with the first image in the sequence

    while running:
        # check for key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    warrior_sequenceID = (warrior_sequenceID + 1) % len(warrior_sprite_sequences)
                    warrior_imageID = 0
                    wizard_sequenceID = (wizard_sequenceID + 1) % len(wizard_sprite_sequences)
                    wizard_imageID = 0
        screen.fill((0,0,0))
        screen.blit(warrior_sprite_sequences[warrior_sequenceID][warrior_imageID], (100, 110)) # Blit the sprite at coordinates (100, 100)
        screen.blit(wizard_sprite_sequences[wizard_sequenceID][wizard_imageID], (400, 50)) # Blit the sprite at coordinates (400, 100)
        pygame.display.flip()
        clock.tick(FPS)
        warrior_imageID = (warrior_imageID + 1) % len(warrior_sprite_sequences[warrior_sequenceID])
        wizard_imageID = (wizard_imageID + 1) % len(wizard_sprite_sequences[wizard_sequenceID])