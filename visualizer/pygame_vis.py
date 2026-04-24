import pygame
import math
import time

#pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill screen with color to wipe away anything from last frame
    screen.fill("blue")

    pygame.draw.circle(screen, "red", player_pos, 40)

    player_pos.y += math.sin(time.time() * 2) * 5
    player_pos.x += math.cos(time.time() * 2) * 5


    # RENDER GAME HERE

    pygame.display.flip()

    clock.tick(60) # RUNS AT 60 FPS

pygame.quit()
