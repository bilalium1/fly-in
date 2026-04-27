import pygame
import colorsys
import math
import time

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

def menu_viz():
    #pygame setup
    hue = 0

    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    clock = pygame.time.Clock()
    running = True

    img = pygame.image.load("crono.jpg").convert()
    img = pygame.transform.scale(img, screen.get_size())
    pygame.font.init()
    big_font = pygame.font.SysFont('Montserrat Black', 50)
    small_font = pygame.font.SysFont('Montserrat Regular', 32)
    i = 0
    current_map = maps[i]
    n_maps = len(maps)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    i = (i + 1) % n_maps
                if event.key == pygame.K_LEFT:
                    i = (i - 1) % n_maps
                current_map = maps[i]
                if event.key == pygame.K_RETURN:
                    return (current_map)

        # fill screen with color to wipe away anything from last frame
        screen.blit(img, (0,0))

        header = big_font.render("WELCOME TO FLY-IN", True, (200,200,200))
        header_sh = big_font.render("WELCOME TO FLY-IN", True, (50,50,80))
        header_hs = big_font.render("WELCOME TO FLY-IN", True, (5,5,8))
        choose = small_font.render("// CHOOSE YOUR MAP", True, (10,10,12))
        diff = small_font.render(current_map.split("/")[1].upper(), True, (10,10,12))
        map = big_font.render(current_map.split("/")[2][:-4].replace("_", " ").upper(), True, (0,0,0))
        credit = small_font.render("B//", True, (10,10,12))
        screen.blit(header_hs, (50, 50 + math.sin(time.time() * 3 - 0.5) * 8))
        screen.blit(header_sh, (50, 50 + math.sin(time.time() * 3 - 0.2) * 8))
        screen.blit(header, (50, 50 + math.sin((time.time()) * 3) * 8))
        screen.blit(choose, (50, 200))
        screen.blit(map, (100, 240))
        screen.blit(diff, (100, 290))

        screen.blit(credit, (50, 450))

        # RENDER GAME HERE

        pygame.display.flip()

        clock.tick(30) # RUNS AT 60 FPS

    pygame.quit()
    return ()
