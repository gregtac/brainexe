import pygame
from pygame import mixer
import os
import random
import csv
import button


pygame.init()

sc_width = 800
sc_height = int(sc_width * 0.8)

screen = pygame.display.set_mode((sc_width, sc_height))
pygame.display.set_caption('BrainExe')

# framerate
clock = pygame.time.Clock()
FPS = 60

# define game variable
gravity = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = sc_height // ROWS
TILE_TYPES = 8
max_levels = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
menu_state = 'main'

# player actions
m_left = False
m_right = False
shoot = False

bgm_load = pygame.mixer.Sound('audio/ost.mp3')
bgm = bgm_load.play(-1, 0, 500)
pygame.mixer.Sound.set_volume(bgm_load, 0.3)

# load images
# button images
start_img = pygame.image.load('imgs/menu/start_button.png').convert_alpha()
options_img = pygame.image.load('imgs/menu/options_button.png').convert_alpha()
credits_img = pygame.image.load('imgs/menu/credits_button.png').convert_alpha()
quit_img = pygame.image.load('imgs/menu/quit_button.png').convert_alpha()
back_img = pygame.image.load('imgs/menu/back_button.png').convert_alpha()
controls_img = pygame.image.load(
    'imgs/menu/controls_button.png').convert_alpha()
restart_img = pygame.image.load('imgs/menu/restart_button.png').convert_alpha()
credits_img = pygame.image.load('imgs/menu/credits_button.png').convert_alpha()
menu_img = pygame.image.load('imgs/menu/menu_button.png').convert_alpha()
music_on_img = pygame.image.load('imgs/menu/music_button.png').convert_alpha()
music_off_img = pygame.image.load(
    'imgs/menu/music_button_off.png').convert_alpha()
# background
veins_img = pygame.image.load('imgs/bg/veins.png').convert_alpha()
vessels_img = pygame.image.load('imgs/bg/vessels.png').convert_alpha()
blood_img = pygame.image.load('imgs/bg/blood.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'imgs/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bullet
bullet_img = pygame.image.load('imgs/icons/bullet1.png').convert_alpha()
bullet2_img = pygame.image.load('imgs/icons/bullet2.png').convert_alpha()
# pick up boxes
ammo_box_img = pygame.image.load('imgs/icons/ammo.png').convert_alpha()
item_boxes = {
    'Ammo': ammo_box_img
}

# colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = blood_img.get_width()
    new_blood_img = pygame.transform.scale(
        blood_img, (width, blood_img.get_height() * 1.15))
    for x in range(4):
        screen.blit(new_blood_img, ((x * width) - bg_scroll * 0.6, -100))
        screen.blit(vessels_img, ((x * width) - bg_scroll * 0.8, 0))

# function to reset level


def reset_level():
    bullet_group.empty()
    item_box_group.empty()
    enemy_group.empty()
    enemy_2_group.empty()
    thorn_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cd = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # create ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for player
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            # reset temporary list
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'imgs/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                image = pygame.image.load(
                    f'imgs/{self.char_type}/{animation}/{i}.png').convert_alpha()
                image = pygame.transform.scale(
                    image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

    def move(self, m_left, m_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0
        # movement variables
        if m_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if m_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -14
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += gravity
        if self.vel_y > 14:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit a wall, turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground; jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above ground; falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with spike
        if pygame.sprite.spritecollide(self, thorn_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off map
        if self.rect.bottom > sc_height:
            self.health = 0

        # check if going off screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > sc_width:
                dx = 0

        # update rect position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > sc_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - sc_width)\
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cd == 0 and self.ammo > 0:
            self.shoot_cd = 20
            bullet = Bullet(self.rect.centerx + (
                0.8 * self.rect.size[0] * self.direction), self.rect.centery - 19, self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # for idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # for idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_m_right = True
                    else:
                        ai_m_right = False
                    ai_m_left = not ai_m_right
                    self.move(ai_m_left, ai_m_right)
                    self.update_action(1)  # for run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (
                        self.rect.centerx + 100 * self.direction, self.rect.centery - 19)
                    pygame.draw.rect(screen, RED, self.vision)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_CD = 120
        # update image depending on current frame
        self.img = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_CD:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation has run out then reset
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.img, self.flip, False), self.rect)


class Enemy2(pygame.sprite.Sprite):
    def __init__(enemy2, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(enemy2)
        enemy2.alive = True
        enemy2.char_type = char_type
        enemy2.speed = speed
        enemy2.ammo = ammo
        enemy2.start_ammo = ammo
        enemy2.shoot_cd = 0
        enemy2.health = 100
        enemy2.max_health = enemy2.health
        enemy2.direction = -1
        enemy2.vel_y = 0
        enemy2.jump = False
        enemy2.in_air = True
        enemy2.flip = False
        enemy2.animation_list = []
        enemy2.frame_index = 0
        enemy2.action = 0
        enemy2.update_time = pygame.time.get_ticks()
        # create ai specific variables
        enemy2.move_counter = 0
        enemy2.vision = pygame.Rect(0, 0, 200, 20)
        enemy2.idling = False
        enemy2.idling_counter = 0

        # load all images for player
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            # reset temporary list
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(
                f'imgs/{enemy2.char_type}/{animation}'))
            for i in range(num_of_frames):
                image = pygame.image.load(
                    f'imgs/{enemy2.char_type}/{animation}/{i}.png').convert_alpha()
                image = pygame.transform.scale(
                    image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                temp_list.append(image)
            enemy2.animation_list.append(temp_list)

        enemy2.img = enemy2.animation_list[enemy2.action][enemy2.frame_index]
        enemy2.rect = enemy2.img.get_rect()
        enemy2.rect.center = (x, y)
        enemy2.width = enemy2.img.get_width()
        enemy2.height = enemy2.img.get_height()

    def update(enemy2):
        enemy2.update_animation()
        enemy2.check_alive()
        # update cooldown
        if enemy2.shoot_cd > 0:
            enemy2.shoot_cd -= 1

    def move(enemy2, m_left, m_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0
        # movement variables
        if m_left:
            dx = -enemy2.speed
            enemy2.flip = True
            enemy2.direction = -1
        if m_right:
            dx = enemy2.speed
            enemy2.flip = False
            enemy2.direction = 1

        # jump
        if enemy2.jump == True and enemy2.in_air == False:
            enemy2.vel_y = -14
            enemy2.jump = False
            enemy2.in_air = True

        # apply gravity
        enemy2.vel_y += gravity
        if enemy2.vel_y > 14:
            enemy2.vel_y
        dy += enemy2.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(enemy2.rect.x + dx, enemy2.rect.y, enemy2.width, enemy2.height):
                dx = 0
                # if the ai has hit a wall, turn around
                if enemy2.char_type == 'enemy_2':
                    enemy2.direction *= -1
                    enemy2.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(enemy2.rect.x, enemy2.rect.y + dy, enemy2.width, enemy2.height):
                # check if below the ground; jumping
                if enemy2.vel_y < 0:
                    enemy2.vel_y = 0
                    dy = tile[1].bottom - enemy2.rect.top
                # check if above ground; falling
                elif enemy2.vel_y >= 0:
                    enemy2.vel_y = 0
                    enemy2.in_air = False
                    dy = tile[1].top - enemy2.rect.bottom

        # check if going off screen
        if enemy2.char_type == 'player':
            if enemy2.rect.left + dx < 0 or enemy2.rect.right + dx > sc_width:
                dx = 0

        # update rect position
        enemy2.rect.x += dx
        enemy2.rect.y += dy

        # update scroll based on player position
        if enemy2.char_type == 'player':
            if (enemy2.rect.right > sc_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - sc_width)\
                    or (enemy2.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                enemy2.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    def shoot(enemy2):
        if enemy2.shoot_cd == 0 and enemy2.ammo > 0:
            enemy2.shoot_cd = 20
            bullet = enemy2_Bullet(enemy2.rect.centerx + (
                0.8 * enemy2.rect.size[0] * enemy2.direction), enemy2.rect.centery + 8, enemy2.direction)
            bullet_group.add(bullet)
            # reduce ammo
            enemy2.ammo -= 1

    def ai(enemy2):
        if enemy2.alive and player.alive:
            if enemy2.idling == False and random.randint(1, 200) == 1:
                enemy2.update_action(0)  # for idle
                enemy2.idling = True
                enemy2.idling_counter = 50
            # check if the ai is near the player
            if enemy2.vision.colliderect(player.rect):
                # stop running and face the player
                enemy2.update_action(0)  # for idle
                # shoot
                enemy2.shoot()
            enemy2.vision.center = (
                enemy2.rect.centerx + 100 * enemy2.direction, enemy2.rect.centery + 8)
            pygame.draw.rect(screen, RED, enemy2.vision)

        # scroll
        enemy2.rect.x += screen_scroll

    def update_animation(enemy2):
        # update animation
        ANIMATION_CD = 120
        # update image depending on current frame
        enemy2.img = enemy2.animation_list[enemy2.action][enemy2.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - enemy2.update_time > ANIMATION_CD:
            enemy2.update_time = pygame.time.get_ticks()
            enemy2.frame_index += 1
        # if animation has run out then reset
        if enemy2.frame_index >= len(enemy2.animation_list[enemy2.action]):
            if enemy2.action == 3:
                enemy2.frame_index = len(
                    enemy2.animation_list[enemy2.action]) - 1
            else:
                enemy2.frame_index = 0

    def update_action(enemy2, new_action):
        # check if new action is different to the previous one
        if new_action != enemy2.action:
            enemy2.action = new_action
            # update the animation settings
            enemy2.frame_index = 0
            enemy2.update_time = pygame.time.get_ticks()

    def check_alive(enemy2):
        if enemy2.health <= 0:
            enemy2.health = 0
            enemy2.speed = 0
            enemy2.alive = False
            enemy2.update_action(3)

    def draw(enemy2):
        screen.blit(pygame.transform.flip(
            enemy2.img, enemy2.flip, False), enemy2.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 1:
                        self.obstacle_list.append(tile_data)
                    elif tile == 2:
                        thorn = Spike(img, x * TILE_SIZE, y * TILE_SIZE)
                        thorn_group.add(thorn)
                    elif tile == 3:
                        item_box = ItemBox(
                            'Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 4:
                        player = Player('player', x * TILE_SIZE,
                                        y * TILE_SIZE, 1, 7, 20)
                        health_bar = HPBar(
                            10, 10, player.health, player.health)
                    elif tile == 5:
                        enemy = Player('enemy', x * TILE_SIZE,
                                       y * TILE_SIZE, 1, 3, 9999)
                        enemy_group.add(enemy)
                    elif tile == 6:
                        enemy_2 = Enemy2('enemy_2', x * TILE_SIZE,
                                         y * TILE_SIZE, 1, 3, 9999)
                        enemy_2_group.add(enemy_2)
                    elif tile == 7:  # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Spike(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y +
                            (TILE_SIZE - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if player has picked up item
        if pygame.sprite.collide_rect(self, player):
            # check what kind of item box
            if self.item_type == 'Ammo':
                player.ammo += 10
            self.kill()


class HPBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class enemy2_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet2_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > sc_width:
            self.kill()
        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 20
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > sc_width:
            self.kill()
        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 20
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(
                screen, self.colour, (0 - self.fade_counter, 0, sc_width // 2, sc_height))
            pygame.draw.rect(screen, self.colour, (sc_width //
                             2 + self.fade_counter, 0, sc_width, sc_height))
            pygame.draw.rect(screen, self.colour, (0, 0 -
                             self.fade_counter, sc_width, sc_height // 2))
            pygame.draw.rect(screen, self.colour, (0, sc_height //
                             2 + self.fade_counter, sc_width, sc_height))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour,
                             (0, 0, sc_width, 0 + self.fade_counter))
        if self.fade_counter >= sc_width:
            fade_complete = True
        return fade_complete


class Timer:
    def __init__(self):
        self.timer_font = pygame.font.SysFont(None, 48)
        self.started = False
        self.elapsed_time = 0

    def start(self):
        self.start_time = pygame.time.get_ticks() - self.elapsed_time
        self.started = True

    def pause(self):
        if self.started:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time
            self.started = False

    def reset(self):
        self.started = False
        self.elapsed_time = 0

    def update(self):
        if self.started:
            current_time = pygame.time.get_ticks()
            self.elapsed_time = current_time - self.start_time
            self.minutes = self.elapsed_time // 60000
            self.seconds = (self.elapsed_time // 1000) % 60
        else:
            self.start_time = pygame.time.get_ticks() - self.elapsed_time

    def draw(self, screen):
        timer_text = self.timer_font.render(
            f"{self.minutes:02d}:{self.seconds:02d}", True, (255, 255, 255))
        timer_rect = timer_text.get_rect()
        timer_rect.topright = (screen.get_width() - 10, 10)
        screen.blit(timer_text, timer_rect)

    def save_time(self):
        csv_file = "time_data.csv"
        # Check if the CSV file exists, create it with a header if it doesn't
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["id", "time"])

        # Read the CSV file to find the previous id
        last_id = 0
        with open(csv_file, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if len(row) > 0 and row[0].isdigit():
                    last_id = int(row[0])

        # Increment the id
        new_id = last_id + 1

        # Save the time, id, and death count
        with open(csv_file, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(
                [new_id, f"{self.minutes:02d}:{self.seconds:02d}"])


time = Timer()
# create screen fades
intro_fade = ScreenFade(1, BLACK, 15)
death_fade = ScreenFade(2, PINK, 15)

# create buttons
start_bttn = button.Button(47, 175, start_img, .80)
options_bttn = button.Button(47, 280, options_img, .5)
credits_bttn = button.Button(47, 350, credits_img, .5)
quit_bttn = button.Button(47, 450, quit_img, 1)
music_bttn = button.Button(345, 200, music_on_img, .8)
keys_bttn = button.Button(287.5, 300, controls_img, .5)
back_bttn = button.Button(280, 380, back_img, 1)
done_bttn = button.Button(
    sc_width // 2.8, sc_height - 75 * 2.3, back_img, 1)
restart_button = button.Button(
    sc_width // 2 - 100, sc_height // 2 - 50, restart_img, 1)


def overlay():
    # Draw a semi-transparent black background
    overlay = pygame.Surface((sc_width, sc_height))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

# This one just draw the "Settings" text on option screen


def draw_options():
    # draw the different options buttons
    font = pygame.font.SysFont("arialblack", 70)
    option_title = font.render("Settings", True, WHITE)
    option_rect = option_title.get_rect()
    option_rect = ((sc_width//3) - 15, (sc_height - 75)//7)
    screen.blit(option_title, option_rect)

# This one draw the keybinds


def draw_keys():
    overlay()
    font = pygame.font.SysFont("arialblack", 70)
    controls = {"Jump": "W", "Left": "A", "Right": "D", "Shoot": "Space"}
    key_font = pygame.font.SysFont("arialblack", 50)
    x = sc_width // 2
    y = (sc_height - len(controls) * 75) // 2
    for key, value in controls.items():
        text = key_font.render(f"{key}: {value}", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        screen.blit(text, text_rect)
        y += 75  # this one is used for the text spacing


def draw_credits():
    overlay()
    # The credit_title is the same as draw_options
    # It's just for writign the "Credits" title]
    font = pygame.font.SysFont("arialblack", 70)
    credit_title = font.render("Credits", True, WHITE)
    credit_rect = credit_title.get_rect()
    credit_rect = (sc_width//3, (sc_height - 100)//10)
    screen.blit(credit_title, credit_rect)

    # Same function as draw_keys / keybinds
    credits = {"April Gem Leo Claudio": "Title", "John Jamel Dagoplo": "Title",
               "Greg Tacuyan": "Title", "David Jarrold Villanueva": "Title"}
    credits_font = pygame.font.SysFont("arialblack", 35)
    x = sc_width // 2
    y = (sc_height - len(credits) * 50) // 2
    for key, value in credits.items():
        text = credits_font.render(f"{key} : {value}", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        screen.blit(text, text_rect)
        y += 45  # text spacing


# Toggle function of music
# This just paused the background music not the stop it
# So if you clicked it, it will just continue where it left off
music_is_toggled = True


def music_toggle(toggle):
    if toggle:
        bgm.unpause()
        music_bttn.image = pygame.transform.scale(
            music_on_img, (music_on_img.get_width() * .8, music_on_img.get_height() * .8))
    else:
        bgm.pause()
        music_bttn.image = pygame.transform.scale(
            music_off_img, (music_off_img.get_width() * .8, music_off_img.get_height() * .8))


def pause_game():
    paused = True
    time.pause()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    time.start()

                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        overlay()
        title_font = pygame.font.SysFont("arialblack", 70)
        desc_font = pygame.font.SysFont("arialblack", 35)

        draw_text("PAUSED", title_font, WHITE,
                  (sc_width//3) - 15, (sc_height - 75)//3)
        draw_text("Press ESC to Continue or Q to Quit",
                  desc_font, WHITE, (sc_width//10), 300)

        pygame.display.update()


# create sprite groups
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_2_group = pygame.sprite.Group()
thorn_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


# temp for create item boxes


# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_bttn.draw(screen):
            start_game = True
            start_intro = True
            time.start()
        if options_bttn.draw(screen):
            menu_state = 'options'
        if credits_bttn.draw(screen):
            menu_state = 'credits'
        if quit_bttn.draw(screen):
            run = False

        # check if the options menu is open
        if menu_state == "options":  # NOTE: 2) This window will appear
            overlay()  # this will create a semi-transparent back-drop
            draw_options()  # "Settings" title
            if music_bttn.draw(screen):
                # change the value either True or False
                music_is_toggled = not music_is_toggled
                music_toggle(music_is_toggled)  # change yung image nung music
            if keys_bttn.draw(screen):
                menu_state = "keys"
            if back_bttn.draw(screen):
                menu_state = "main"

        if menu_state == "keys":  # keybind window
            draw_keys()
            if done_bttn.draw(screen):
                menu_state = "options"

        if menu_state == "credits":  # credits window
            draw_credits()
            if done_bttn.draw(screen):
                menu_state = "main"

    else:

        # update bg
        draw_bg()
        # draw world map
        world.draw()
        # show player health
        health_bar.draw(player.health)
        # show ammo
        draw_text(f'AMMO: {player.ammo}', font, WHITE, 10, 35)

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        for enemy_2 in enemy_2_group:
            enemy_2.ai()
            enemy_2.update()
            enemy_2.draw()

        # update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)
        thorn_group.update()
        thorn_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)

        time.update()
        time.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
            time.start()

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2)  # 2 is jump
            elif m_left or m_right:
                player.update_action(1)  # 1 is run
            else:
                player.update_action(0)  # 0 is idle
            screen_scroll, level_complete = player.move(m_left, m_right)
            bg_scroll -= screen_scroll
            # check if player has completed level
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= max_levels:
                    start_intro = True
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                else:
                    time.save_time()

        else:
            time.reset()
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    time.start()
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # quits game
        if event.type == pygame.QUIT:
            run = False

        # keybinds/controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                m_left = True
            if event.key == pygame.K_d:
                m_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE and start_game:
                time.started = not time.started
                pause_game()

        # when button is not pressed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                m_left = False
            if event.key == pygame.K_d:
                m_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
