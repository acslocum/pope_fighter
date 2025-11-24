from audio_loader import GameSounds
from enum import Enum
import pygame
import os
import random
from sprite_loader import *
from PopeData import PopeData

class Actions(Enum):
    ATTACK = 0
    ATTACK2 = 1
    DEATH = 2
    HIT = 3
    IDLE = 4
    VICTORY = 5
    WALKING = 6
class Fighter:
    def __init__(self, player, x, y, flip, directory, sound : GameSounds, pope : PopeData = None):
        self.player = player
        self.popeData : PopeData = pope 
        self.flip = flip
        self.offset : list[tuple[int]] = []
        self.loadedScales : list[int] = []
        self.animation_list : list[list[pygame.Surface]] = self.load_images(directory)
        self.image_scale = 1
        self.action = Actions.IDLE.value  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.size = self.image.get_height() # probably should change to actual size, or fix spritesheets so sprites are square
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, int(240 * self.image_scale * self.loadedScales[self.action]), int(480 * self.image_scale) * self.loadedScales[self.action]))
        if self.flip:
            self.rect.x = self.rect.x - 240 * self.image_scale
        self.attacking_rect = self.rect
        self.vel_y = 0
        self.running = False
        # self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound : GameSounds = sound
        self.hit = False
        self.alive = True
        self.victory = False

        self.debug = False

        # pope specifc mods, we've got 4 and they'll all effect aspects of play:
        #  - holiness -> maximum health
        #  - miracles -> defense rating (chance to block dmg)
        #  - wisdom   -> attack rating (chance to hit)
        #  - legacy   -> attack power (amount of dmg done per hit)
        # these stats naturally range from 3-9, but can get bumped to 10 by solving puzzles
        self.averageStat = 6
        self.holiness = self.averageStat
        self.miracles = self.averageStat
        self.wisdom = self.averageStat
        self.legacy = self.averageStat
        if pope is not None:
            self.holiness = pope.holiness
            self.miracles = pope.miracles
            self.wisdom = pope.wisdom
            self.legacy = pope.legacy
        self.health = 100 * (1 + (self.holiness - self.averageStat) / 10)
        self.max_health = self.health # hold their max health, so we can draw health bar correctly
        #print(f'Pope {player} initial health: {self.health} / {self.max_health}')
        #self.print_stats()

    def print_stats(self):
        name = ''
        if self.popeData is None:
            name = 'Player ' + str(self.player)
        else:
            name = self.popeData.name

        print(f'{name}: h={self.holiness}, m={self.miracles}, w={self.wisdom}, l={self.legacy}')

    def load_images(self, directory) -> list[list[pygame.Surface]]:
        # parse description file and then load sprites from their spritesheets
        # print(f'Loading sprites from {directory}')
        desc_filename = 'descriptions.txt' # there should be one of these at the top of each character dir
        sheet_filename = 'spritesheet.png' # should be called this for all actions

        desc_file = os.path.join(directory, desc_filename)
        descriptions = parseDescriptionFile(desc_file)
        #print(f'Player {self.player} descriptions: {descriptions}')

        sprites = []
        for action in descriptions:
            self.offset.append( (descriptions[action]['x_off'], descriptions[action]['y_off']) )
            self.loadedScales.append(descriptions[action]['scale'])
            action_dir = os.path.join(directory, action)
            sprite_file = os.path.join(action_dir, sheet_filename)

            sprite_layout = (descriptions[action]['columns'], descriptions[action]['rows']) # columns, rows - might not be complete
            num_sprites = descriptions[action]['count']

            spritesheet = pygame.image.load(sprite_file).convert_alpha()
            action_sprites = get_sequence(spritesheet, sprite_layout, num_sprites)

            sprites.append(action_sprites)

        # print(f'Player {self.player} offsets: {self.offset}')
        return sprites

    def move(self, screen_width, screen_height, target, round_over):
        SPEED = int(0.005 * screen_width)
        GRAVITY = int(0.005 * screen_height)
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # get keypresses
        key = pygame.key.get_pressed()

        # can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:
            # check player 1 controls
            if self.player == 1:
                # movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                # jump
                # if key[pygame.K_w] and self.jump == False:
                #     self.vel_y = -30
                #     self.jump = True
                # attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            # check player 2 controls
            if self.player == 2:
                # movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                # jump
                # if key[pygame.K_UP] and self.jump == False:
                #     self.vel_y = -30
                #     self.jump = True
                # attack
                if key[pygame.K_m] or key[pygame.K_n]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_m]:
                        self.attack_type = 1
                    if key[pygame.K_n]:
                        self.attack_type = 2

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        screen_bottom_offset = screen_height * 0.2
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - screen_bottom_offset:
            self.vel_y = 0
            # self.jump = False
            dy = screen_height - screen_bottom_offset - self.rect.bottom

        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

        # update attack rect
        self.attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                2 * self.rect.width, self.rect.height)

    # handle animation updates
    def update(self):
        # check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(Actions.DEATH.value)  # 6:death
            if self.attack_sound is not None:
                effect = self.attack_sound.getRandEffect('dying')
                effect.play()
        elif self.hit:
            self.update_action(Actions.HIT.value)  # 5:hit
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(Actions.ATTACK.value)  # 3:attack1
            elif self.attack_type == 2:
                self.update_action(Actions.ATTACK2.value)  # 4:attack2
        elif self.victory:
            self.update_action(Actions.VICTORY.value)  # 2:victory
        elif self.running:
            self.update_action(Actions.WALKING.value)  # 1:run
        else:
            self.update_action(Actions.IDLE.value)  # 0:idle

        animation_cooldown = 50
            #print(f'Ticks: {pygame.time.get_ticks()}')
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            # if the player is dead then end the animation
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # check if an attack was executed
                if self.action == Actions.ATTACK.value or self.action == Actions.ATTACK2.value:
                    self.attacking = False
                    self.attack_cooldown = 20
                # check if damage was taken
                if self.action == Actions.HIT.value:
                    self.hit = False
                    # if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            if self.attack_sound is not None:
                effect = self.attack_sound.getRandEffect('attack')
                effect.play()

            if self.attacking_rect.colliderect(target.rect):
                # need to calculate whether hit occurs, and if so
                # how much dmg is done based on player stats
                #  - miracles -> defense rating (chance to block dmg)
                #      default value of 6 -> 30% chance to block, +/- 5% per step off from 6
                #  - wisdom   -> attack rating (chance to hit)
                #      default value of 6 -> 70% chance to hit, +/- 5% per step off from 6
                #  - legacy   -> attack power (amount of dmg done per hit)
                #       dmg per hit will be +/- 2 of your legacy value (i.e. legacy = 6 can do 4-8 dmg)
                block_pct = 0.3 + 0.05 * (target.miracles - self.averageStat)
                block_roll = random.uniform(0.0, 1.0)
                block = True if block_roll <= block_pct else False
                print(f'block% {block_pct:.2f}, block roll {block_roll:.4f}, block? {block}')
                hit_pct = 0.7 + 0.05 * (self.wisdom - self.averageStat)
                hit_roll = random.uniform(0.0, 1.0)
                hit = True if hit_roll <= hit_pct else False
                print(f'hit% {hit_pct:.2f}, hit roll {hit_roll:.4f}, hit? {hit}')
                dmg_rng = (self.legacy - 2, self.legacy + 2)
                dmg_roll = random.randrange(dmg_rng[0], dmg_rng[1]+1)
                if block == False and hit == True:
                    print(f'Hit! dmg done: {dmg_roll} from {dmg_rng}')
                    target.health -= dmg_roll
                    target.hit = True
                    if target.health <= 0:
                        self.victory = True
                else:
                    print('No hit')

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            # if new_action == Actions.HIT.value:
            #     print(f'Starting hit action: {pygame.time.get_ticks()}')
            # elif self.action == Actions.HIT.value:
            #     print(f'End hit action: {pygame.time.get_ticks()}')
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        scale = self.loadedScales[self.action]
        img = pygame.transform.smoothscale(img, (img.get_width() * scale, img.get_height() * scale))
        if 0 <= self.action < len(self.offset):
            offset = self.offset[self.action]
        else:
            offset = (0,0)
        #print(f'Fighter::draw: offset: {offset}')
        x_off = offset[0]
        if self.flip:
            x_off = img.get_width() - x_off * self.loadedScales[self.action] - self.rect.width * self.loadedScales[self.action] 
        surface.blit(img, (self.rect.x - (x_off * self.image_scale * self.loadedScales[self.action]), self.rect.y - (offset[1] * self.image_scale * self.loadedScales[self.action])))
        if self.debug:
            # draw a circle at sprite center and a hit box
            #print('Drawing indicators')
            center = (self.rect.centerx, self.rect.centery)
            pygame.draw.circle(surface, (255,255,255), center, 5)
            pygame.draw.rect(surface, (255,0,0), self.rect, width = 1)
            pygame.draw.rect(surface, (255,255,0), self.attacking_rect, width = 1)

    def draw_health_bar(self, screen : pygame.Surface, rect : pygame.Rect, flip : bool = False):
        BLACK = (0,0,0)
        RED = (255,0,0)
        YELLOW = (255,255,0)
        GREEN = (0,255,0)
        WHITE = (255,255,255)
        x = rect.x
        y = rect.y
        x_off = 0
        health_pct = self.health / self.max_health
        health_width = int(rect.width * health_pct) # width in pixels to draw health
        if flip:
            x_off = rect.width - health_width
        #print(f'{x}, {y}, {health_width}, {rect.height}')
        #print(f'{health_pct}')

        # draw everything
        pygame.draw.rect(screen, BLACK, rect)
        if 0 < health_pct <= 0.25:
            pygame.draw.rect(screen, RED, (x + x_off, y, health_width, rect.height))
        elif 0.25 < health_pct <= 0.50:
            pygame.draw.rect(screen, YELLOW, (x + x_off, y, health_width, rect.height))
        elif 0.50 < health_pct:
            pygame.draw.rect(screen, GREEN, (x + x_off, y, health_width, rect.height))
        pygame.draw.rect(screen, WHITE, rect, 2)