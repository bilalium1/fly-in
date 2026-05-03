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

# your story list
lines = [
    "Chrono Trigger",
    "",
    "",
    "Hear now the chronicle of ages, as told in the echoes of Chrono Trigger...",
    "In the year of festivity, beneath banners and ringing bells, there walked a youth named Crono.",
    "By chance—or by the will of time itself—he met the maiden Marle, whose laughter concealed a royal fate.",
    "Lo, a gate was torn open by man’s curious hand, and the flow of time was broken.",
    "Thus began the journey.",
    "Through the ages they wandered.",
    "To a kingdom lost in mist, where a queen’s fate unraveled.",
    "To a future laid to waste, where the skies were ash and sorrow.",
    "To an age of magic, where floating cities touched the heavens and pride reached too far.",
    "There, in the shadow of gods, slept the destroyer: Lavos.",
    "A being not born of this world, whose coming would mark the end of all things.",
    "Heroes gathered, as if summoned by the threads of destiny.",
    "The knight Frog, bound by honor and grief.",
    "The mind of iron, Robo, who learned the weight of a soul.",
    "The wild flame, Ayla, of an age before memory.",
    "And the fallen mage, Magus, whose vengeance shaped the tides of fate.",
    "Together, they stood against the end.",
    "Time itself was bent.",
    "Lives lost were reclaimed, or left as sacrifice.",
    "Kingdoms rose and fell in a single breath.",
    "And the truth was revealed.",
    "That even the smallest moment can echo across eternity.",
    "At the last, beneath a dying sky, they faced Lavos.",
    "A battle not for power, but for the right of the world to continue.",
    "The clash shook the fabric of time itself, as past and future trembled as one.",
    "In that final moment, hope burned brighter than the dying stars above.",
    "And when the darkness fell, silence claimed the world for a fleeting breath.",
    "Then—light returned, carried by the will of those who dared to defy fate.",
    "Time began anew, its flow restored, yet forever changed by their struggle.",
    "And so the script fades, its final lines unwritten.",
    "For time is not a single path, but many.",
    "Some endings bring reunion, others quiet parting beneath open skies.",
    "But in every thread of time, their journey lives on.",
    "And the ending is yours to choose."
    "",
    "B//"
]

# --- INIT ---
def manoria():
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
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in lines]

    # starting y (bottom of screen)
    y_offset = HEIGHT

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
                    from visualizer.menu_vis import menu_viz
                    pygame.mixer.music.fadeout(1000)
                    time.sleep(1)
                    pygame.quit()
                    menu_viz()

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