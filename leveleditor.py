import pygame
import button
import csv
import os

path = "C:\\Users\\third\\Desktop\\capstone"
os.chdir(path)

#import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
screen_width = 800
screen_height = 640
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((screen_width + side_margin, screen_height + lower_margin))
pygame.display.set_caption('Level Editor')

#game vars
rows = 16
max_cols = 150
tile_size = screen_height // rows
tile_types = 8
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1



#images
veins = pygame.image.load('imgs/bg/veins.png').convert_alpha()
vessels = pygame.image.load('imgs/bg/vessels.png').convert_alpha()
blood = pygame.image.load('imgs/bg/blood.png').convert_alpha()
#function for drawing bground

#store tile in list
img_list = []
for x in range (tile_types):
    img = pygame.image.load(f'imgs/tile/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

save_img = pygame.image.load('imgs/save_btn.png').convert_alpha()
load_img = pygame.image.load('imgs/load_btn.png').convert_alpha()

#color def
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

font = pygame.font.SysFont('Futura', 30)

#create empty tile list
world_data = []
for row in range(rows):
    r = [-1] * max_cols
    world_data.append(r)

#create ground
for tile in range(0, max_cols):
    world_data[rows - 1][tile] = 0


#function for outputting text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))



def draw_bg():
    screen.fill(white)
    width = veins.get_width()
    for x in range (4):
        screen.blit(veins, ((x * width)-scroll * 0.5, 0))
        screen.blit(vessels, ((x * width)-scroll * 0.6, screen_height - vessels.get_height() - 350))
        screen.blit(blood, ((x * width)-scroll * 0.7, screen_height - blood.get_height() + 400))

def draw_grid():
    #vertical lines
    for c in range(max_cols + 1):
        pygame.draw.line(screen, black,(c * tile_size - scroll, 0),(c * tile_size - scroll, screen_height))
    #horizontal
    for c in range(rows + 1):
        pygame.draw.line(screen, black,(0, c * tile_size),(screen_width, c * tile_size ))

#function for drawing world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile],(x * tile_size - scroll, y * tile_size))
  
#create buttons
save_button = button.Button(screen_width // 2, screen_height + lower_margin - 50, save_img, 1)
load_button = button.Button(screen_width // 2 + 200, screen_height + lower_margin - 50, load_img, 1)
#make button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(screen_width + (75 * button_col)+50, 75*button_row+50,img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0



run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, white, 10, screen_height + lower_margin - 90)
    draw_text('Press Up or Down to change level', font, white, 10, screen_height + lower_margin - 60)

    #save and load data
    if save_button.draw(screen):
        #save level data
        #pickle_out = open(f'level{level}_data,', 'wb')
        #pickle.dump(world_data, pickle_out)
        #pickle_out.close()
        with open(f'level{level}_data.csv', 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for row in world_data:
                writer.writerow(row)
    if load_button.draw(screen):
        #load level data
        #reset scroll back to the level
        scroll = 0
        #world_data = []
        #pickle_in = open(f'level{level}_data,', 'rb')
        #world_data = pickle.load(pickle_in)
        with open(f'level{level}_data.csv', newline = '') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
                

    #draw tile panel
    pygame.draw.rect(screen, green, (screen_width, 0, side_margin, screen_height))

    #choose tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    #highlight selected tile
    pygame.draw.rect(screen, red, button_list[current_tile].rect, 3)

    #scroll map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (max_cols * tile_size) - screen_width:
        scroll += 5 * scroll_speed

    #add new tiles to screen
    #get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // tile_size
    y = pos[1] // tile_size

    #check if coordinates are within tile area
    if pos[0] < screen_width and pos[1] < screen_height:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1
    pygame.display.update()
pygame.quit()
