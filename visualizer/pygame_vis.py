import pygame
import colorsys
import math
import time
import os

def get_map_rect(SCALE, Y_SCALE, info):

    X = max([nfo[0] for h, nfo in info['hubs'].items()])
    Y = max([nfo[1] for h, nfo in info['hubs'].items()])
    
    return ((X * SCALE) + SCALE, (Y * (SCALE + Y_SCALE)) + SCALE)

def viz(info):
    #pygame setup
    hue = 0

    SCALE = 100
    Y_SCALE = 20

    SCREEN_X = 1300
    SCREEN_Y = 800

    pygame.mixer.music.stop()
    pygame.mixer.music.load("sounds/Determination.mp3")
    pygame.mixer.music.play(loops=-1)

    map_rect = get_map_rect(SCALE, Y_SCALE, info)

    while (map_rect[0] > SCREEN_X - 100):
        SCALE -= 5
        map_rect = get_map_rect(SCALE, Y_SCALE, info)
    
    while (map_rect[1] > SCREEN_Y - 100):
        SCALE -= 5
        Y_SCALE -= 1
        map_rect = get_map_rect(SCALE, Y_SCALE, info)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    clock = pygame.time.Clock()
    running = True

    img = pygame.image.load("images/crono.jpg").convert()
    img = pygame.transform.scale(img, screen.get_size())
    img.set_alpha(50)
    pygame.font.init()

    epoch = pygame.image.load("images/epoch.png")
    epoch = pygame.transform.scale(epoch, (180, 150))

    offset = pygame.Vector2(0,0)

    center_pos = pygame.Vector2(SCREEN_X // 2 - map_rect[0] // 2 + SCALE // 3, SCREEN_Y // 2 - map_rect[1] // 2 + SCALE)
    my_font = pygame.font.SysFont('misc/ChronoType.ttf', 20)
    big_font = pygame.font.SysFont('misc/ChronoType.ttf', 40)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

        # fill screen with color to wipe away anything from last frame  
        screen.blit(img, (0,0))
        offset = pygame.Vector2(math.cos(time.time()) * 10, math.sin(time.time()) * 10)

        for cn1, cn2, max_link in info["connections"]:
            start_pos = pygame.Vector2(
                center_pos.x + info["hubs"][cn1][0] * SCALE,
                center_pos.y + info["hubs"][cn1][1] * (SCALE + Y_SCALE)) + offset
            end_pos = pygame.Vector2(
                center_pos.x + info["hubs"][cn2][0] * SCALE,
                center_pos.y + info["hubs"][cn2][1] * (SCALE + Y_SCALE)) + offset
            pygame.draw.line(screen, 'black', start_pos, end_pos, SCALE // 40 + 2)
            pygame.draw.line(screen, 'white', start_pos, end_pos, SCALE // 40)

        for hub, nfo in info["hubs"].items():
            x = center_pos.x + (nfo[0] * SCALE)
            y = center_pos.y + (nfo[1] * (SCALE + Y_SCALE))
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
            screen.blit(text, pos + pygame.Vector2(-15,-6))

        #title = big_font.render(info["map_path"].split("/")[2].replace("_"," ").upper()[:-4], True, (255,255,255))
        #diff = big_font.render(info["map_path"].split("/")[1].upper(), True, (200,200,200))
        max_drones = my_font.render("Number of Drones : " + str(info["nb_drones"]), True, (150, 150, 180))
        #screen.blit(title, (50, 50))
        #screen.blit(diff, (50, 100))
        screen.blit(max_drones, (50, 150))
        screen.blit(epoch, (100, 100))


        # RENDER GAME HERE

        pygame.display.flip()

        clock.tick(60) # RUNS AT 60 FPS
        
    pygame.quit()
