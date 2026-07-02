import pygame
import sys
import time

# --- CONFIG ---
WIDTH, HEIGHT = 1000, 600
FPS = 60

BG_IMAGE = "images/story.jpg"   # your image
MUSIC_FILE = "sounds/manoria_orch.mp3"      # your music
FONT_FILE = "misc/ChronoType.ttf"              # or "font.ttf"
FONT_SIZE = 24
SCROLL_SPEED = 0.18

# --- INIT ---

with open("misc/chrono_story.txt", "r") as f:
    lines = f.readlines()


def manoria() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chrono Story")
    clock = pygame.time.Clock()

    # background
    bg = pygame.image.load(BG_IMAGE)
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    # font
    font = pygame.font.Font(FONT_FILE, FONT_SIZE)

    # music
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.play(-1)

    # prepare text surfaces
    text_surfaces = [font.render(
        line, True, (255, 255, 255)) for line in lines]

    # starting y (bottom of screen)
    y_offset = float(HEIGHT)

    smaller_font = pygame.font.Font('misc/ChronoType.ttf', 21)

    keys_story = smaller_font.render("[ R ] -> Return", True, (200, 200, 220))
    keys_quit = smaller_font.render("[ Q ] -> Quit", True, (200, 200, 220))

    # --- LOOP ---
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    from visualizer.menu_vis import MenuViz
                    pygame.mixer.music.fadeout(1000)
                    time.sleep(1)
                    pygame.quit()
                    MenuViz()

        # draw background
        screen.blit(bg, (0, 0))

        # draw scrolling text
        # draw scrolling text (centered)
        y = y_offset
        for surf in text_surfaces:
            rect = surf.get_rect(center=(WIDTH // 2, y))
            screen.blit(surf, rect)
            y += surf.get_height() + 10

        # move text upward
        y_offset -= SCROLL_SPEED

        # reset when finished
        if y < 0:
            y_offset = HEIGHT

        pygame.draw.rect(screen, (200, 200, 240), (850, 40, 125, 55), 0, 5)
        pygame.draw.rect(screen, (5, 5, 15), (850, 35, 125, 55), 0, 5)

        screen.blit(keys_story, (865, 45))
        screen.blit(keys_quit, (865, 65))

        pygame.display.flip()

    pygame.quit()
    sys.exit()
