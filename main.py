import pygame
from pygame import *
from pygame.locals import *
from pygame.sprite import *
from PIL import Image, ImageSequence
import random
import sys

pygame.init()
# pygame.mixer.init()

"""
How to put scores, lives, etc... on the screen
variable_name = font.render(f"Score: " {score}, True, (255, 255, 255)) # third arg: colour
screen.blit(variable_name, (20, 20)) # second arg: location
"""

# Screen
screen = pygame.display.set_mode((640, 480))

# Music
# pygame.mixer.music.load("background_music.mp3")
# pygame.mixer.music.play(-1)
# pygame.mixer.music.set_volume(0.3)

# click_effect = pygame.mixer.Sound("click_effect.mp3")
# click_effect.set_volume(0.6)

# click_effect.play()

# Clock
clock = pygame.time.Clock()

# Colours
white = (255,255,255)
black = (0,0,0)

# GIFS
def load_gif(path, size):
    gif = Image.open(path)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        frame = frame.resize(size, Image.LANCZOS)
        pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
        frames.append(pygame_frame)
    return frames

# Sprites
class SpriteMoving(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, fps=8):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.fps = fps
        self.timer = 0
    def update(self, dt):
        self.timer = self.timer + dt
        if self.timer >= 1000/self.fps:
            self.timer = 0
            self.frame_index = min(self.frame_index+1, len(self.frames) - 1)
            self.image = self.frames[self.frame_index]
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class player(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        super().__init__()
#        pygame.sprite.Sprite.__init__(self)
#        self.image = pygame.image.load("main_standing.png").convert_alpha()
#        self.image = pygame.transform.scale(self.image, (92, 72))

        self.standing_image = pygame.image.load("main_right.png").convert_alpha()
        self.standing_image = pygame.transform.scale(self.standing_image, (92, 72))

        self.jump_image = pygame.image.load("main_jump_right.png").convert_alpha()
        self.jump_image = pygame.transform.scale(self.jump_image, (92, 72))

        self.image = self.standing_image
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.xvelocity = 0
        self.yvelocity = 0 
        self.grounded = False
        
    def update(self, platforms):
        
        self.prev_y = self.rect.y # used for collision detection, so that player does not go through platform
        self.prev_x = self.rect.x # used for collision detection, so that player does not go through platform
        
        self.xvelocity = 0
        
        keys = pygame.key.get_pressed() # checks if any keys are pressed
        
        if keys[pygame.K_LEFT]: # moving left
            self.xvelocity = -5

        if keys[pygame.K_RIGHT]: # moving right
            self.xvelocity = 5

        if keys[pygame.K_UP] and self.grounded: # jumping
            self.yvelocity = -15
        
        self.yvelocity += 0.5 # gravity
        
        self.rect.x += self.xvelocity
        
        self.grounded = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.xvelocity > 0:
                    self.rect.right = platform.rect.left
                if self.xvelocity < 0:
                    self.rect.left = platform.rect.right
        
        self.rect.y += self.yvelocity
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.prev_y + self.rect.height <= platform.rect.top: 
                    self.rect.bottom = platform.rect.top
                    self.yvelocity = 0
                    self.grounded = True
                elif self.prev_y >= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.yvelocity = 0
        
        if not self.grounded:
            self.image = self.jump_image
        else:
            self.image = self.standing_image
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Platform(pygame.sprite.Sprite):
    
    def __init__(self, color, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        # self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Item(pygame.sprite.Sprite):
    
    def __init__(self, color, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self, players):
        
        global number_of_coins
    
        player_collisions = pygame.sprite.spritecollide(self, players, dokill = False)
        
        for player in player_collisions:
            number_of_coins += 1
            print("collision")
            self.kill()
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
# Wrap text in box
def wrapped_text(surface, text, font, color, x, y, max_width):
    words = text.split(" ")
    line = ""
    line_height = font.get_linesize()
    
    for word in words:
        text_line = line + word + " "
        if font.size(text_line)[0] <= max_width:
            line = text_line
        else:
            surface.blit(font.render(line, True, color), (x, y))
            y = y + line_height
            line = word + " "
    screen.blit(font.render(line, True, color), (x, y))

# Riddles

riddle_answer = ""
user_riddle = ""
riddle_number = 0

def given_riddle(riddle_number):
    if riddle_number == 0:
        riddle_number = random.randint(1,16)
    if riddle_number >= 1 and riddle_number <= 16:
        riddle_number = riddle_number + 1
    if riddle_number == 17:
        riddle_number = 1
        
    if riddle_number == 1:
        user_riddle = "I follow you all the time and copy your every move, but you can't touch or catch me? What am I?"
        riddle_answer = "shadow"
        return user_riddle, riddle_answer
    elif riddle_number == 2:
        user_riddle = "What can't talk but will reply when spoken to?"
        riddle_answer = "echo"
        return user_riddle, riddle_answer
    elif riddle_number == 3:
        user_riddle = "What gets bigger when more is taken away?"
        riddle_answer = "hole"
        return user_riddle, riddle_answer
    elif riddle_number == 4:
        user_riddle = "I'm light as a feather, yet the strongest person can't hold me for five minutes. What am I?"
        riddle_answer = "breath"
        return user_riddle, riddle_answer
    elif riddle_number == 5:
        user_riddle = "If you've got me, you want to share me; if you share me, you haven't kept me. What am I?"
        riddle_answer = "secret"
        return user_riddle, riddle_answer
    elif riddle_number == 6:
        user_riddle = "The more of this there is, the less you see. What am I?:"
        riddle_answer = "darkness" or "dark" or "fog"
        return user_riddle, riddle_answer
    elif riddle_number == 7:
        user_riddle = "Where does today come before yesterday?: "
        riddle_answer = "dictionary"
        return user_riddle, riddle_answer
    elif riddle_number == 8:
        user_riddle = "What is full of holes but still holds water?"
        riddle_answer = "sponge"
        return user_riddle, riddle_answer
    elif riddle_number == 9:
        user_riddle = "I go all around the world, but never leave the corner. What am I?"
        riddle_answer = "stamp"
        return user_riddle, riddle_answer
    elif riddle_number == 10:
        user_riddle = "It belongs to you, but other people use it more than you do. What is it?:"
        riddle_answer = "name"
        return user_riddle, riddle_answer
    elif riddle_number == 11:
        user_riddle = "What comes once in a minute, twice in a moment, but never in a thousand years?:"
        riddle_answer = "m"
        return user_riddle, riddle_answer
    elif riddle_number == 12:
        user_riddle = "What has a head and a tail, but no body?"
        riddle_answer = "coin"
        return user_riddle, riddle_answer
    elif riddle_number == 13:
        user_riddle = "The shorter I am, the bigger I am. What am I?"
        riddle_answer = "temper"
        return user_riddle, riddle_answer
    elif riddle_number == 14:
        user_riddle = "I am so simple that I can only point, yet I guide people all over the world. What am I?"
        riddle_answer = "compass"
        return user_riddle, riddle_answer
    elif riddle_number == 15:
        user_riddle = "What has many keys but can't open a single lock?:"
        riddle_answer = "piano"
        return user_riddle, riddle_answer
    elif riddle_number == 16:
        user_riddle = "Bob's dad has three children: Snap, Crackle, and ...:"
        riddle_answer = "bob"
        return user_riddle, riddle_answer

# Doors
def doors():
    good_door = int(random.randint(1,3))
    riddle_door = int(random.randint(1,3))
    bad_door = int(random.randint(1,3))
    
    while good_door == riddle_door:
        riddle_door = int(random.randint(1,3))
    
    while bad_door == good_door or bad_door == riddle_door:
        bad_door = int(random.randint(1,3))
    
    return good_door, bad_door, riddle_door

# Draw rectangle
def draw_rect(screen, color, alpha, rect_position):
    x, y, width, height = rect_position
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    rgba_color = (*color, alpha)
    temp_surface.fill(rgba_color)
    screen.blit(temp_surface, (x, y))
    return pygame.Rect(rect_position)

# Import Screens

title_screen_bg = pygame.image.load("title_screen.png").convert()
title_screen = pygame.transform.scale(title_screen_bg, (640, 480))

difficulties_screen_bg = pygame.image.load("difficulty_screen.gif").convert()
difficulties_screen = pygame.transform.scale(difficulties_screen_bg, (640, 480))

genie_intro = pygame.image.load("genie_talk.gif").convert()
genie_intro = pygame.transform.scale(genie_intro, (640, 480))

genie_lose = pygame.image.load("genie_lose.gif").convert()
genie_lose = pygame.transform.scale(genie_lose, (640, 480))

genie_good = pygame.image.load("genie_good.gif").convert()
genie_good = pygame.transform.scale(genie_good, (640, 480))

door_screen_bg = pygame.image.load("choose_door.png").convert()
door_screen = pygame.transform.scale(door_screen_bg, (640, 480))

good_door_bg = pygame.image.load("good_door_bg.gif")
good_door_bg = pygame.transform.scale(good_door_bg, (640, 480))

riddle_door_bg = pygame.image.load("riddle_door_bg.png")
riddle_door_bg = pygame.transform.scale(riddle_door_bg, (640, 480))

bad_door_bg = pygame.image.load("bad_door_bg.png")
bad_door_bg = pygame.transform.scale(bad_door_bg, (640, 480))

lost_a_life_bg = pygame.image.load("lost_a_life_bg.png")
lost_a_life_bg = pygame.transform.scale(lost_a_life_bg, (640, 480))

do_nothing_bg = pygame.image.load("do_nothing_bg.png")
do_nothing_bg = pygame.transform.scale(do_nothing_bg, (640, 480))

give_coins_bg = pygame.image.load("give_coins.png")
give_coins_bg = pygame.transform.scale(give_coins_bg, (640, 480))

backstory_no_looping_frames = pygame.image.load("backstory_no_looping.gif").convert()
backstory_bg = pygame.transform.scale(backstory_no_looping_frames, (640, 480))

backstory_door_bg = pygame.image.load("backstory_door_bg.png")
backstory_door_bg = pygame.transform.scale(backstory_door_bg, (640, 480))

riddle_door_wrong_bg = pygame.image.load("riddle_door_wrong.png")
riddle_door_wrong = pygame.transform.scale(riddle_door_wrong_bg, (640, 480))

riddle_door_correct_bg = pygame.image.load("riddle_door_correct.png")
riddle_door_correct = pygame.transform.scale(riddle_door_correct_bg, (640, 480))

menu_list_bg = pygame.image.load("menu.png")
menu_list = pygame.transform.scale(menu_list_bg, (640, 480))

menu_button = pygame.image.load("menu_button.png")
menu_button = pygame.transform.scale(menu_button, (123, 42))

# Animations
frame_difficulties = load_gif("difficulty_screen.gif", (640, 480))
frame_index_difficulties = 0

frame_backstory = load_gif("backstory_no_looping.gif", (640, 480))
frame_index_backstory = 0

frame_genie_intro = load_gif("genie_talk.gif", (640, 480))
frame_index_intro = 0

frame_genie_good = load_gif("genie_good.gif", (640, 480))
frame_index_good = 0

frame_genie_lose = load_gif("genie_lose.gif", (640, 480))
frame_index_lose = 0

# Doors
green_door = pygame.image.load("green_door.png").convert_alpha()
green_door = pygame.transform.scale(green_door, (250,300))

blue_door = pygame.image.load("blue_door.png").convert_alpha()
blue_door = pygame.transform.scale(blue_door, (250, 300))

red_door = pygame.image.load("red_door.png").convert_alpha()
red_door = pygame.transform.scale(red_door, (250, 300))

# Cup
cup_bg = pygame.image.load("cup.png").convert_alpha()
cup = pygame.transform.scale(cup_bg, (150,150))

# Main character
main_standing_left = pygame.image.load("main_left.png").convert_alpha()
main_standing_left = pygame.transform.scale(main_standing_left, (184, 144))

main_standing_right = pygame.image.load("main_right.png").convert_alpha()
main_standing_right = pygame.transform.scale(main_standing_right, (184, 144))

main_jump_left = pygame.image.load("main_jump_left.png").convert_alpha()
main_jump_left = pygame.transform.scale(main_jump_left, (184, 144))

main_jump_right = pygame.image.load("main_jump_right.png").convert_alpha()
main_jump_right = pygame.transform.scale(main_jump_right, (184, 144))

main_running_left_frames = load_gif("main_running_left.gif", (184, 144))
main_running_left = SpriteMoving(main_running_left_frames, x = 130, y = 65, fps = 12)

main_running_right_frames = load_gif("main_running_right.gif", (184, 144))
main_running_right = SpriteMoving(main_running_right_frames, x = 130, y = 65, fps = 12)

# Gold Coin animation gif
gold_coin_frames = load_gif("gold_coin.gif", (100, 100))

# Level 1 Coins in Good Door
gold_coin_l1_1 = SpriteMoving(gold_coin_frames, x = 200, y = 15, fps = 50)
gold_coin_l1_2 = SpriteMoving(gold_coin_frames, x = 25, y = 175, fps = 50)
gold_coin_l1_3 = SpriteMoving(gold_coin_frames, x = 125, y = 350, fps = 50)
gold_coin_l1_4 = SpriteMoving(gold_coin_frames, x = 550, y = 150, fps = 50)
gold_coin_l1_5 = SpriteMoving(gold_coin_frames, x = 250, y = 275, fps = 50)

# Level 2 Coins in Good Door ** change locations (harder)
gold_coin_l2_1 = SpriteMoving(gold_coin_frames, x = 200, y = 15, fps = 50)
gold_coin_l2_2 = SpriteMoving(gold_coin_frames, x = 25, y = 175, fps = 50)
gold_coin_l2_3 = SpriteMoving(gold_coin_frames, x = 125, y = 350, fps = 50)
gold_coin_l2_4 = SpriteMoving(gold_coin_frames, x = 550, y = 150, fps = 50)
gold_coin_l2_5 = SpriteMoving(gold_coin_frames, x = 250, y = 275, fps = 50)

# keisha, make level 3 and beyond gold coins

# Elevator state
elevator_y = 260
elevator_direction = 1  # 1 means down, -1 means up
elevator_min_y = 260
elevator_max_y = 440

# Backstory timer
backstory_start_time = pygame.time.get_ticks()
backstory_duration = 8000
backstory_frame_timer = 0
backstory_frame_fps = 2

# Correct riddle timer
correct_start_time = pygame.time.get_ticks()
correct_duration = 9000

#Game code; important variables
running = True

current_screen = "title"

font = pygame.font.SysFont("Times New Roman", 21)

riddle_number = 0
return_value = None
user_answer = ""

# Noah's stuff

BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

p1 = player(120, 264)
item1 = Item(YELLOW, 20, 20, 160, 80)
item2 = Item(GREEN, 20, 20, 120, 80)
item3 = Item(RED, 20, 20, 80, 80)
platform1 = Platform(BLUE, 239, 30, 0, 263)
platform2 = Platform(BLUE, 160, 30, 377, 266)
platform3 = Platform(RED, 23, 320, 366, 126)
platform4 = Platform(GREEN, 434, 30, 107, 101)
top_barrier = Platform(BLUE, 640, 1, 0, 0)
bottom_barrier = Platform(BLACK, 640, 50, 0, 446)
left_barrier = Platform(BLUE, 1, 480, 0, 0)
right_barrier = Platform(BLUE, 1, 480, 640, 0)

players = pygame.sprite.Group()
players.add(p1)

platforms = pygame.sprite.Group()
platforms.add(platform1)
platforms.add(platform2)
platforms.add(platform3)
platforms.add(platform4)
platforms.add(bottom_barrier)
platforms.add(left_barrier)
platforms.add(right_barrier)
platforms.add(top_barrier)

items = pygame.sprite.Group()
items.add(item1)
items.add(item2)
items.add(item3)


number_of_coins = 0
while running:
    # Other Variables
    dt = clock.tick(60)
    
    # On the title screen
    if current_screen == "title":
        screen.blit(title_screen, (0,0))
        
        # buttons to click for start
        start_button = draw_rect(screen, (0, 0, 0), 0, (42, 250, 190, 60))
        score_button = draw_rect(screen, (0, 0, 0), 0, (44, 345, 190, 60))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
    
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT: # stops programs
                running = False
        
            if current_screen == "title":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if menu_rect.collidepoint(event.pos):
                            current_screen = "menu_list"
                            previous_screen = "title"
                            # click_effect.play()
                            break
                        if start_button.collidepoint(event.pos):
                            current_screen = "backstory"
                            # click_effect.play()
                            break
                    
                        if score_button.collidepoint(event.pos):
                            current_screen = "score"
                            # click_effect.play()
                            break
                            # code about retrieving information from a file and printing (design screen)

    if current_screen == "backstory":
        
        lives = 0
        coins = 0
        doors_passed = 0
        
        backstory_current_time = pygame.time.get_ticks()
        
        if frame_index_backstory == 0 and backstory_frame_timer == 0:
            backstory_start_time = backstory_current_time
        
        if backstory_current_time - backstory_start_time < backstory_duration:
            screen.fill(white)
            screen.blit(frame_backstory[frame_index_backstory], (0,0))
            
            # Update frame timing
            backstory_frame_timer += dt
            if backstory_frame_timer >= 1000 / backstory_frame_fps:
                backstory_frame_timer = 0
                frame_index_backstory = min(frame_index_backstory + 1, len(frame_backstory) - 1)
            
            skip_button = draw_rect(screen, (0, 0, 0), 0, (30, 43, 106, 42))
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if skip_button.collidepoint(event.pos):
                            current_screen = "difficulties"
                            # click_effect.play()
                            break
    
        else:
            screen.fill(white)
            screen.blit(backstory_door_bg, (0,0))
            
            start_button_2 = draw_rect(screen, (0, 0, 0), 0, (30, 43, 106, 42))
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if start_button_2.collidepoint(event.pos):
                            current_screen = "difficulties"
                            # click_effect.play()
                            break
    
    if current_screen == "difficulties":
        screen.fill(white)
        
        screen.blit(frame_difficulties[frame_index_difficulties], (0,0))
        frame_index_difficulties = (frame_index_difficulties + 1) % len(frame_difficulties)
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        easy_button = draw_rect(screen, (0, 0, 0), 0, (30, 142, 200, 75))
        medium_button = draw_rect(screen, (0, 0, 0), 0, (30, 255, 200, 75))
        hard_button = draw_rect(screen, (0, 0, 0), 0, (30, 368, 200, 75))

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "difficulties"
                        # click_effect.play()
                        break
                    if easy_button.collidepoint(event.pos):
                        lives = 6
                        current_screen = "choose_door"
                        difficulty = 1
                        # click_effect.play()
                        break
                    if medium_button.collidepoint(event.pos):
                        lives = 4
                        current_screen = "choose_door"
                        difficulty = 2
                        # click_effect.play()
                        break
                    if hard_button.collidepoint(event.pos):
                        lives = 3
                        current_screen = "choose_door"
                        difficulty = 3
                        # click_effect.play()
                        break
 
    if current_screen == "choose_door":
        screen.blit(door_screen, (0, 0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
    
        left_door_button = draw_rect(screen, (0, 0, 0), 200, (80, 115, 150, 250))
        mid_door_button = draw_rect(screen, (0, 0, 0), 200, (250, 115, 150, 250))
        right_door_button = draw_rect(screen, (0, 0, 0), 200, (420, 115, 150, 250))
        
        screen.blit(green_door, (30,65))
        screen.blit(red_door, (200,65))
        screen.blit(blue_door, (370,65))
        
        good_door = int(random.randint(1,3))
        riddle_door = int(random.randint(1,3))
        bad_door = int(random.randint(1,3))
        
        while good_door == riddle_door:
            riddle_door = int(random.randint(1,3))
        
        while bad_door == good_door or bad_door == riddle_door:
            bad_door = int(random.randint(1,3))
            
        if good_door == 1:
            good_door = left_door_button
        elif good_door == 2:
            good_door = mid_door_button
        else:
            good_door = right_door_button
        
        if bad_door == 1:
            bad_door = left_door_button
        elif bad_door == 2:
            bad_door = mid_door_button
        else:
            bad_door = right_door_button
            
        if riddle_door == 1:
            riddle_door = left_door_button
        elif riddle_door == 2:
            riddle_door = mid_door_button
        else:
            riddle_door = right_door_button
            
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "choose_door"
                        # click_effect.play()
                        break
                    if left_door_button.collidepoint(event.pos):
                        # click_effect.play()
                        if good_door == left_door_button:
                            current_screen = "good_door"
                            break
                        if bad_door == left_door_button:
                            current_screen = "bad_door"
                            break
                        if riddle_door == left_door_button:
                            current_screen = "riddle_door"
                            break
                    if mid_door_button.collidepoint(event.pos):
                        if good_door == mid_door_button:
                            current_screen = "good_door"
                            break
                        if bad_door == mid_door_button:
                            current_screen = "bad_door"
                            break
                        if riddle_door == mid_door_button:
                            current_screen = "riddle_door"
                            break
                    if right_door_button.collidepoint(event.pos):
                        if good_door == right_door_button:
                            current_screen = "good_door"
                            break
                        if right_door_button == bad_door:
                            current_screen = "bad_door"
                            break
                        if right_door_button == riddle_door:
                            current_screen = "riddle_door"
                            break
        # set lives
        # set timer
    
    if current_screen == "good_door":
        screen.fill(white)
        screen.blit(good_door_bg, (0, 0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "good_door"
                        # click_effect.play()
                        break

        p1.update(platforms)
        items.update(players)
        
        p1.draw(screen)
    
        for platform in platforms:
            platform.draw(screen)
    
        for item in items:
            item.draw(screen)
        
        # Boundaries with the platforms
        # horizontal__left_platform = draw_rect(screen, (0, 0, 0), 0, (0, 263, 245, 35))
        # horizontal_top_platform = draw_rect(screen, (0, 0, 0), 0, (100, 100, 450, 35))
        # horizontal_right_platform = draw_rect(screen, (0, 0, 0), 0, (360, 264, 183, 35))
        # vertical_right_platform = draw_rect(screen, (0, 0, 0), 0, (360, 100, 35, 400))
        
        # platform

        elevator = draw_rect(screen, (91, 91, 90), 255, (245, elevator_y, 115, 35))
        
        # Elevator state
        # if level == 1:
        #     elevator_speed = 1
        # elif level == 2:
        #     elevator_speed = 1.5
        # elif level == 3:
        #     elevator_speed = 2
        # elif level == 4:
        #     elevator_speed = 2.5
        # elif level >= 5:
        #     elevator_speed = 3
        
        elevator_speed = 1 # temporary speed
        
        elevator_y += elevator_speed * elevator_direction
        
        if elevator_y <= elevator_min_y or elevator_y >= elevator_max_y:
            elevator_direction *= -1

        # screen.blit(gold_coin_l1_1, (200, 15))
        # screen.blit(gold_coin_l1_2, (25, 175))
        # screen.blit(gold_coin_l1_3, (125, 350))
        # screen.blit(gold_coin_l1_4, (550, 150))
        # screen.blit(gold_coin_l1_5, (250, 275))
        
        # if main_standing.colliderect(current_gold_coin):
            # 
        
    if current_screen == "bad_door":
        
        screen.fill(white)
        screen.blit(bad_door_bg, (0, 0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        left_ghost_button = draw_rect(screen, (0, 0, 0), 0, (17, 230, 155, 300))
        middle_ghost_button = draw_rect(screen, (0, 0, 0), 0, (235, 235, 155, 300))
        right_ghost_button = draw_rect(screen, (0, 0, 0), 0, (460, 225, 155, 300))
        
        take_life_ghost = int(random.randint(1,3))
        do_nothing_ghost = int(random.randint(1,3))
        coins_ghost = int(random.randint(1,3))
        
        while take_life_ghost == do_nothing_ghost:
            do_nothing_ghost = int(random.randint(1,3))
        
        while coins_ghost == take_life_ghost or coins_ghost == do_nothing_ghost:
            coins_ghost = int(random.randint(1,3))
        
        if take_life_ghost == 1:
            take_life_ghost = left_ghost_button
        elif take_life_ghost == 2:
            take_life_ghost = middle_ghost_button
        else:
            take_life_ghost = right_ghost_button
        
        if do_nothing_ghost == 1:
            do_nothing_ghost = left_ghost_button
        elif do_nothing_ghost == 2:
            do_nothing_ghost = middle_ghost_button
        else:
            do_nothing_ghost = right_ghost_button
            
        if coins_ghost == 1:
            coins_ghost = left_ghost_button
        elif coins_ghost == 2:
            coins_ghost = middle_ghost_button
        else:
            coins_ghost = right_ghost_button
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "bad_door"
                        # click_effect.play()
                        break
                    if left_ghost_button.collidepoint(event.pos):
                        # click_effect.play()
                        if take_life_ghost == left_ghost_button:
                            current_screen = "take_life"
                        if do_nothing_ghost == left_ghost_button:
                            current_screen = "do_nothing"
                        if coins_ghost == left_ghost_button:
                            current_screen = "give_coins"
                        break
                    
                    if middle_ghost_button.collidepoint(event.pos):
                        # click_effect.play()
                        if take_life_ghost == middle_ghost_button:
                            current_screen = "take_life"
                        if do_nothing_ghost == middle_ghost_button:
                            current_screen = "do_nothing"
                        if coins_ghost == middle_ghost_button:
                            current_screen = "give_coins"
                        break
                    
                    if right_ghost_button.collidepoint(event.pos):
                        # click_effect.play()
                        if take_life_ghost == right_ghost_button:
                            current_screen = "take_life"
                        if do_nothing_ghost == right_ghost_button:
                            current_screen = "do_nothing"
                        if coins_ghost == right_ghost_button:
                            current_screen = "give_coins"
                        break
    
    if current_screen == "take_life":
        
        lives -= 1
        
        backstory_current_time = pygame.time.get_ticks()
        
        if backstory_current_time - backstory_start_time < backstory_duration:
            screen.fill(white)
            screen.blit(lost_a_life_bg, (0, 0))
            screen.blit(menu_button, (510, 20))
            menu_rect = draw_rect(screen, (0, 0, 0), 200, (510, 20, 123, 42))
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if menu_rect.collidepoint(event.pos):
                            current_screen = "menu_list"
                            previous_screen = "take_life"
                            # click_effect.play()
                            break
            
        else:
            current_screen = "choose_door_easy"
    
    if current_screen == "do_nothing":
        
        backstory_current_time = pygame.time.get_ticks()
        
        if backstory_current_time - backstory_start_time < backstory_duration:
            screen.fill(white)
            screen.blit(do_nothing_bg, (0, 0))
            screen.blit(menu_button, (510, 20))
            menu_rect = draw_rect(screen, (0, 0, 0), 200, (510, 20, 123, 42))
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if menu_rect.collidepoint(event.pos):
                            current_screen = "menu_list"
                            previous_screen = "do_nothing"
                            # click_effect.play()
                            break
            
        else:
            current_screen = "choose_door_easy"
    
    if current_screen == "give_coins":
        
        backstory_current_time = pygame.time.get_ticks()
        
        if backstory_current_time - backstory_start_time < backstory_duration:
            screen.fill(white)
            screen.blit(give_coins_bg, (0, 0))
            screen.blit(menu_button, (510, 20))
            menu_rect = draw_rect(screen, (0, 0, 0), 200, (510, 20, 123, 42))
            
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if menu_rect.collidepoint(event.pos):
                            current_screen = "menu_list"
                            previous_screen = "do_nothing"
                            # click_effect.play()
                            break
            
        else:
            current_screen = "choose_door_easy"
    
    if current_screen == "riddle_door":
        
        correct_current_time = pygame.time.get_ticks()
        
        screen.fill(white)
        screen.blit(riddle_door_bg, (0, 0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        while not return_value:
            return_value = given_riddle(riddle_number)
 
        user_riddle, riddle_answer = return_value
        
        wrapped_text(screen, user_riddle, font, black, 230, 100, 375)
        
        user_response = font.render(user_answer, True, black)
        screen.blit(user_response, (230, 200))
        print(user_answer)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # click_effect.play()
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "riddle_door"
                        break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_answer = user_answer[:-1]
                elif event.key == pygame.K_RETURN:
                    user_answer = user_answer.lower()
                    if user_answer == riddle_answer:
                        current_screen = "correct_answer"
                    else:
                        current_screen = "wrong_answer"
                    break
                else:
                    user_answer = user_answer + event.unicode
        
        print(current_screen)
        
    if current_screen == "correct_answer":
        return_value = None
        user_answer = ""
        coins = coins + 8
        
        screen.fill(white)
        screen.blit(riddle_door_correct, (0,0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        continue_button = draw_rect(screen, (0,0,0), 0, (8, 42, 123, 42))
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # click_effect.play()
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "choose_door"
                        break
                    if continue_button.collidepoint(event.pos):
                        if difficulty == 1:
                            current_screen = "choose_door"
                            break
                        if difficulty == 2:
                            current_screen = "choose_door"
                            break
                        if difficulty == 3:
                            current_screen = "choose_door"
                            break
    
    if current_screen == "wrong_answer":
        lives -= 1
        
        return_value = None
        user_answer = ""
        
        screen.fill(white)
        screen.blit(riddle_door_wrong, (0,0))
        
        screen.blit(menu_button, (510, 20))
        menu_rect = draw_rect(screen, (0, 0, 0), 0, (510, 20, 123, 42))
        
        continue_button = draw_rect(screen, (0,0,0), 0, (8, 42, 123, 42))
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # click_effect.play()
                    if menu_rect.collidepoint(event.pos):
                        current_screen = "menu_list"
                        previous_screen = "choose_door"
                        break
                    if continue_button.collidepoint(event.pos):
                        if difficulty == 1:
                            current_screen = "choose_door_easy"
                            break
                        if difficulty == 2:
                            current_screen = "choose_door_medium"
                            break
                        if difficulty == 3:
                            current_screen = "choose_door_hard"
                            break

    if current_screen == "menu_list":
        screen.fill(white)
        screen.blit(menu_list, (0,0))
        
        continue_button = draw_rect(screen, (0,0,0), 0, (65, 140, 505, 100))
        quit_button = draw_rect(screen, (0,0,0), 0, (65, 250, 505, 100))
        restart_button = draw_rect(screen, (0,0,0), 0, (65, 360, 505, 100))
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # click_effect.play()
                if event.button == 1:
                    if continue_button.collidepoint(event.pos):
                        current_screen = previous_screen
                        break
                    if quit_button.collidepoint(event.pos):
                        running = False
                        break
                    if restart_button.collidepoint(event.pos):
                        current_screen = "title"
                        break
    
    pygame.display.flip()

pygame.quit()
