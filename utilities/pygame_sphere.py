import pygame

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('3D-like sphere')

img = pygame.image.load('utilities/red_cape.png').convert_alpha()
scaled_img = pygame.transform.smoothscale(img, (100,100))
print(f'image size: ({img.get_width(), img.get_height()})')

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)

sphere_center = (width // 2, height // 2)
sphere_radius = 100
num_shades = 50

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    screen.blit(scaled_img, (sphere_center[0] - scaled_img.get_width()//2, sphere_center[1] - scaled_img.get_height() // 2))

    surface1 = pygame.Surface((width,height))
    surface1.set_colorkey((0,0,0))
    surface1.set_alpha(80)

    for i in range(num_shades, 0, -1):
        current_radius = int(sphere_radius * (i / num_shades))
        color_component = int(255 * (1 - (i / num_shades)))
        current_color = (255 - color_component, 0, 0)
        pygame.draw.circle(surface1, current_color, sphere_center, current_radius)

    screen.blit(surface1, (0,0))
    pygame.display.flip()

pygame.quit