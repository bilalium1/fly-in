import colorsys
import math
import random
import time

import pygame

from visualizer.manoria_vis import manoria

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
    "maps/challenger/01_the_impossible_dream.txt",
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
    '"Even in despair, there is a path forward." -Schala',
]

chrono_font = "misc/ChronoType.ttf"
pixel_font = "misc/Pixeltype.ttf"
heav_font = "misc/upheavtt.ttf"


def loop_y(t, screen_h, speed=1.0):
    return (t * speed * screen_h) % (screen_h + 500)


class MenuViz:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((800, 500))
        self.clock = pygame.time.Clock()
        self.running = True

        pygame.display.set_caption("Fly-In Trigger")
        pygame.display.set_icon(pygame.image.load("images/chronoIcon.png"))

        pygame.mixer.music.load("sounds/menu.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_pos(0.5)

        self.select_sound = pygame.mixer.Sound("sounds/blipSelect.wav")
        self.enter_sound = pygame.mixer.Sound("sounds/Enter.wav")
        self.select_sound.set_volume(0.2)
        self.enter_sound.set_volume(0.4)

        self.img = pygame.image.load("images/crono.jpg").convert()
        self.img = pygame.transform.scale(self.img, self.screen.get_size())

        self.epoch = pygame.image.load("images/epoch.png")
        self.epoch = pygame.transform.scale(self.epoch, (120, 100))
        self.epoch.set_alpha(200)

        pygame.font.init()
        self.big_font = pygame.font.Font(heav_font, 50)
        self.small_font = pygame.font.Font(chrono_font, 32)
        self.smaller_font = pygame.font.Font(pixel_font, 21)
        self.smallest_font = pygame.font.Font(pixel_font, 16)

        self.hue = 0

        self.m_pos = pygame.Vector2(150, 260)

        self.i = 0
        self.n_maps = len(maps)
        self.current_map = maps[self.i]

        self.chosen_quote = quotes[random.randint(0, len(quotes) - 1)]

    def create_star(
        self, points, cx, cy, outer_radius, inner_radius, inner: bool, rot: float
    ):
        if points < 2:
            points = 10
            inner_radius = outer_radius
        vertices = []
        if inner:
            for i in range(points * 2):
                angle = math.pi / 2 + i * math.pi / points
                radius = outer_radius if i % 2 == 0 else inner_radius

                x = cx + math.cos(angle + rot) * radius
                y = cy - math.sin(angle + rot) * radius

                vertices.append((x, y))

        else:
            for i in range(points):
                angle = math.pi / 2 + i * (2 * math.pi / points)

                x = cx + math.cos(angle + rot) * outer_radius
                y = cy - math.sin(angle + rot) * outer_radius

                vertices.append((x, y))

        return vertices

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.m_pos += pygame.Vector2(20, 0)
                        self.select_sound.play()
                        self.i = (self.i + 1) % self.n_maps

                    if event.key == pygame.K_UP:
                        self.m_pos += pygame.Vector2(20, 0)
                        self.select_sound.play()
                        self.i = (self.i - 1) % self.n_maps

                    self.current_map = maps[self.i]

                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.fadeout(300)
                        self.enter_sound.play()
                        self.enter_sound.set_volume(0.1)
                        time.sleep(0.3)
                        return self.current_map

                    if event.key == pygame.K_s:
                        manoria()

                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return None

            # draw
            self.screen.blit(self.img, (0, 0 + math.sin(time.time()) * 8))

            self.hue += 0.01

            y = loop_y(time.time(), self.screen.get_height(), speed=0.05)
            self.screen.blit(self.epoch, (450, y - 200))

            header = self.big_font.render("WELCOME TO FLY-IN", True, (200, 200, 200))
            header_sh = self.big_font.render("WELCOME TO FLY-IN", True, (50, 50, 80))
            header_hs = self.big_font.render("WELCOME TO FLY-IN", True, (5, 5, 8))

            choose = self.small_font.render("// CHOOSE YOUR MAP", True, (10, 10, 12))

            difficulty = self.current_map.split("/")[1].upper()

            r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)

            diff_colors = {
                "EASY": "green3",
                "MEDIUM": "orange",
                "HARD": "crimson",
                "CHALLENGER": (int(r * 255), int(g * 255), int(b * 255)),
            }

            diff = self.big_font.render(difficulty, True, diff_colors[difficulty])
            diff_shadow = self.big_font.render(difficulty, True, "black")

            map_txt = self.big_font.render(
                self.current_map.split("/")[2][:-4].replace("_", " ").upper(),
                True,
                (0, 0, 0),
            )

            n_map = self.small_font.render(
                maps[(self.i + 1) % self.n_maps]
                .split("/")[2][:-4]
                .replace("_", " ")
                .upper(),
                True,
                (0, 0, 0),
            )

            nn_map = self.smaller_font.render(
                maps[(self.i + 2) % self.n_maps]
                .split("/")[2][:-4]
                .replace("_", " ")
                .upper(),
                True,
                (0, 0, 0),
            )

            self.m_pos = self.m_pos.lerp((150, 270), 0.2)

            quote = self.smaller_font.render(self.chosen_quote, True, (10, 10, 12))
            credit = self.small_font.render("B//", True, (10, 10, 12))

            keys_story = self.smaller_font.render(
                "[ S ] -> Story", True, (200, 200, 220)
            )
            keys_quit = self.smaller_font.render("[ Q ] -> Quit", True, (200, 200, 220))

            star = self.create_star(
                8, 70, 60 + math.sin(time.time() * 3 - 0.5) * 8, 120, 60, True, self.hue
            )
            star2 = self.create_star(
                8,
                70,
                60 + math.sin(time.time() * 3 - 0.5) * 8,
                50,
                30,
                True,
                self.hue * 2,
            )

            star3 = self.create_star(8, self.m_pos.x - 50, 280, 90, 65, True, self.hue)
            star4 = self.create_star(8, self.m_pos.x - 50, 280, 50, 40, True, self.hue)

            pygame.draw.polygon(self.screen, "black", star, 2)
            pygame.draw.polygon(self.screen, "lightblue1", star2, 0)
            pygame.draw.polygon(self.screen, "lightblue2", star3, 0)
            pygame.draw.polygon(self.screen, "black", star3, 3)
            pygame.draw.polygon(self.screen, diff_colors[difficulty], star4, 3)

            n_map.set_alpha(100)
            nn_map.set_alpha(70)

            self.screen.blit(header_hs, (50, 50 + math.sin(time.time() * 3 - 0.5) * 8))
            self.screen.blit(header_sh, (50, 50 + math.sin(time.time() * 3 - 0.2) * 8))
            self.screen.blit(header, (50, 50 + math.sin(time.time() * 3) * 8))

            self.screen.blit(choose, (50, 200))
            self.screen.blit(map_txt, self.m_pos)
            self.screen.blit(diff_shadow, self.m_pos + (-100, -35))
            self.screen.blit(diff, self.m_pos + (-100, -38))
            self.screen.blit(n_map, (130, 320))
            self.screen.blit(nn_map, (125, 350))

            pygame.draw.rect(self.screen, (200, 200, 240), (650, 40, 125, 55), 0, 5)
            pygame.draw.rect(self.screen, (5, 5, 15), (650, 35, 125, 55), 0, 5)

            self.screen.blit(keys_story, (665, 45))
            self.screen.blit(keys_quit, (665, 65))

            self.screen.blit(quote, (50, 100))
            self.screen.blit(credit, (50, 450))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        return None
