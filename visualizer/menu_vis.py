import pygame
import colorsys
import math
import time
import random

maps = [
    "maps/easy/01_linear_path.txt",
    "maps/easy/02_simple_fork.txt",
    "maps/easy/03_basic_capacity.txt",

    "maps/medium/01_dead_end_trap.txt",
    "maps/medium/02_circular_loop.txt",
    "maps/medium/03_priority_puzzle.txt",

    "maps/hard/01_maze_nightmare.txt",
    "maps/hard/02_capacity_hell.txt",
    "maps/hard/03_ultimate_challenge.txt",

    "maps/challenger/01_the_impossible_dream.txt"
]

quotes = [
    '"But... the future refused to change." -Magus',
    '"The right time is anytime you feel like it." -Crono',
    '"To change history, you must first change yourself." -Gaspar',
    '"I am the wind… the sea… and the sky." -Schala',
    '"The future is not written. It can be changed." -Lucca',
    '"What do you think? Should we change history?" -Marle',
    '"We must hurry… or the past will be lost forever." -Frog',

    '"All life begins with Nu and ends with Nu..." -Spekkio',
    '"Power is not something that is given. It is taken." -Magus',
    '"A strong will can change even fate itself." -Crono',
    '"Time flows like a river, and history is its current." -Gaspar',
    '"The world is full of possibilities… even the impossible ones." -Lucca',
    '"I fight not for glory, but for those I cannot save otherwise." -Frog',
    '"Even in despair, there is a path forward." -Schala'
]

import math

def loop_y(t, screen_h, speed=1.0):
    return (t * speed * screen_h) % (screen_h + 500)

def menu_viz():
    #pygame setup
    hue = 0

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 500))
    clock = pygame.time.Clock()
    running = True

    pygame.display.set_caption("Fly-In Trigger")
    pygame.display.set_icon(pygame.image.load("images/chronoIcon.png"))

    pygame.mixer.music.load("sounds/menu_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)

    select_sound = pygame.mixer.Sound("sounds/blipSelect.wav")
    select_sound.set_volume(0.2)

    img = pygame.image.load("images/crono.jpg").convert()
    img = pygame.transform.scale(img, screen.get_size())

    epoch = pygame.image.load("images/epoch.png")
    epoch = pygame.transform.scale(epoch, (120, 100))
    epoch.set_alpha(200)

    pygame.font.init()
    big_font = pygame.font.Font('misc/ChronoType.ttf', 50)
    small_font = pygame.font.Font('misc/ChronoType.ttf', 32)
    smaller_font = pygame.font.Font('misc/ChronoType.ttf', 21)
    i = 0
    current_map = maps[i]
    n_maps = len(maps)

    chosen_quote = quotes[random.randint(0, len(quotes)-1)]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    select_sound.play()
                    i = (i + 1) % n_maps
                if event.key == pygame.K_UP:
                    select_sound.play()
                    i = (i - 1) % n_maps
                current_map = maps[i]
                if event.key == pygame.K_RETURN:
                    return (current_map)
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return (None)

        # fill screen with color to wipe away anything from last frame
        screen.blit(img, (0,0))
        y = loop_y(time.time(), screen.get_height(), speed=0.05)
        screen.blit(epoch, (450, y - 200))

        header = big_font.render("WELCOME TO FLY-IN", True, (200,200,200))
        header_sh = big_font.render("WELCOME TO FLY-IN", True, (50,50,80))
        header_hs = big_font.render("WELCOME TO FLY-IN", True, (5,5,8))
        choose = small_font.render("// CHOOSE YOUR MAP", True, (10,10,12))
        diff = small_font.render(current_map.split("/")[1].upper(), True, (10,10,12))
        map = big_font.render(current_map.split("/")[2][:-4].replace("_", " ").upper(), True, (0,0,0))
        n_map = small_font.render(maps[(i + 1) % n_maps].split("/")[2][:-4].replace("_", " ").upper(), True, (0,0,0))
        nn_map = small_font.render(maps[(i + 2) % n_maps].split("/")[2][:-4].replace("_", " ").upper(), True, (0,0,0))
        quote = smaller_font.render(chosen_quote, True, (10,10,12))
        credit = small_font.render("B//", True, (10,10,12))

        n_map.set_alpha(100)
        nn_map.set_alpha(70)
        screen.blit(header_hs, (50, 50 + math.sin(time.time() * 3 - 0.5) * 8))
        screen.blit(header_sh, (50, 50 + math.sin(time.time() * 3 - 0.2) * 8))
        screen.blit(header, (50, 50 + math.sin((time.time()) * 3) * 8))
        screen.blit(choose, (50, 200))
        screen.blit(map, (100, 240))
        screen.blit(diff, (100, 290))
        screen.blit(n_map, (100, 330))
        screen.blit(nn_map, (100, 370))

        screen.blit(quote, (50, 100))
        screen.blit(credit, (50, 450))

        # RENDER GAME HERE

        pygame.display.flip()

        clock.tick(30) # RUNS AT 60 FPS

    pygame.quit()
    return (None)
