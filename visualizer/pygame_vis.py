import pygame
import colorsys
import math
import time

def get_furthest_x(curr_scale, info, screen_x, screen_y):

    X = max([nfo[0] for h, nfo in info['hubs'].items()])
    Y = max([nfo[1] for h, nfo in info['hubs'].items()])

    while (X * curr_scale > screen_x - 50):
        curr_scale -= 5

    while (Y * curr_scale > screen_y - screen_y // 2):
        curr_scale -= 5
    
    return curr_scale

def viz(info):
    #pygame setup
    hue = 0

    SCALE = 80
    Y_SCALE = 20

    SCREEN_X = 1300
    SCREEN_Y = 800

    SCALE = get_furthest_x(SCALE, info, SCREEN_X, SCREEN_Y)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    clock = pygame.time.Clock()
    running = True

    img = pygame.image.load("crono.jpg").convert()
    img = pygame.transform.scale(img, screen.get_size())
    img.set_alpha(10)
    pygame.font.init()

    offset = pygame.Vector2(0,0)

    player_pos = pygame.Vector2(100, screen.get_height() / 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill screen with color to wipe away anything from last frame
        screen.blit(img, (0,0))
        my_font = pygame.font.SysFont('Montserrat Bold', 21)
        texts = []

        offset = pygame.Vector2(math.cos(time.time()) * 10, math.sin(time.time()) * 10)

        for cn1, cn2 in info["connections"]:
            start_pos = pygame.Vector2(
                player_pos.x + info["hubs"][cn1][0] * SCALE,
                player_pos.y + info["hubs"][cn1][1] * (SCALE + Y_SCALE)) + offset
            end_pos = pygame.Vector2(
                player_pos.x + info["hubs"][cn2][0] * SCALE,
                player_pos.y + info["hubs"][cn2][1] * (SCALE + Y_SCALE)) + offset
            pygame.draw.line(screen, 'black', start_pos, end_pos, SCALE // 40 + 2)
            pygame.draw.line(screen, 'white', start_pos, end_pos, SCALE // 40)

        for hub, nfo in info["hubs"].items():
            x = player_pos.x + (nfo[0] * SCALE)
            y = player_pos.y + (nfo[1] * (SCALE + Y_SCALE))
            pos = pygame.Vector2(x, y) + offset
            color = nfo[2]['color']
            zone = nfo[2]['zone']
            max_dones = nfo[2]['max_drones']
            pygame.draw.circle(screen, 'black', pos, SCALE // 3 + 4)
            pygame.draw.circle(screen, 'white', pos, SCALE // 3 + 2)
            if color == 'rainbow':
                hue += 0.01
                r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                color = (int(r*255), int(g*255), int(b*255))
                pygame.draw.circle(screen, color, pos, SCALE // 3)
            else:
                pygame.draw.circle(screen, color, pos, SCALE // 3)
            text = my_font.render(zone.upper()[0] + "/" + str(max_dones), False, (255,255,255) if color == 'black' else (0,0,0))
            screen.blit(text, pos + pygame.Vector2(-10,-6))


        # RENDER GAME HERE

        pygame.display.flip()

        clock.tick(60) # RUNS AT 60 FPS
        
    pygame.quit()
