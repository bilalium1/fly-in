import pygame
import math
import time

def viz(info):
    #pygame setup
    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    clock = pygame.time.Clock()
    running = True

    player_pos = pygame.Vector2(120, screen.get_height() / 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill screen with color to wipe away anything from last frame
        screen.fill("black")

        for hub, nfo in info["hubs"].items():
            x = player_pos.x + (nfo[0] * 80)
            y = player_pos.y + (nfo[1] * 80)
            pos = pygame.Vector2(x, y)
            pygame.draw.circle(screen, nfo[2], pos, 20)

        # RENDER GAME HERE

        pygame.display.flip()

        clock.tick(60) # RUNS AT 60 FPS

    pygame.quit()
