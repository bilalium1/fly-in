import colorsys
import math
import random
import time
from pathlib import Path
import pygame
from typing import List, Union

from visualizer.manoria_vis import manoria

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

chrono_font = "fonts/ChronoType.ttf"
pixel_font = "fonts/Pixeltype.ttf"
heav_font = "fonts/upheavtt.ttf"

Color = Union[str, tuple[int, int, int]]


def loop_y(t: float, screen_h: int, speed: float) -> float:
    return (t * speed * screen_h) % (screen_h + 500)


class MenuViz:
    def __init__(self) -> None:
        # INIT PYGAME AND MIXER
        pygame.init()
        pygame.mixer.init()

        # INIT SCREEN AND CLOCK
        self.screen = pygame.display.set_mode((1000, 500))
        self.clock = pygame.time.Clock()
        self.running = True

        # CHANGE WINDOW TITLE AND ICON
        pygame.display.set_caption("Fly-In Trigger")
        pygame.display.set_icon(pygame.image.load("images/chronoIcon.png"))

        # LOAD MUSIC
        pygame.mixer.music.load("sounds/menu.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_pos(0.5)

        # LOAD SOUND EFFECTS
        self.select_sound = pygame.mixer.Sound("sounds/blipSelect.wav")
        self.enter_sound = pygame.mixer.Sound("sounds/Enter.wav")
        self.select_sound.set_volume(0.2)
        self.enter_sound.set_volume(0.4)

        # LOAD BACKGROUND IMAGE
        self.img = pygame.image.load("images/crono.jpg").convert()
        self.img = pygame.transform.scale(self.img, self.screen.get_size())

        # LOAD EPOCH (SPACESHIP)
        self.epoch = pygame.image.load("images/epoch.png")
        self.epoch = pygame.transform.scale(self.epoch, (120, 100))
        self.epoch.set_alpha(200)

        self.pfp = pygame.image.load("images/pfp.png")
        self.pfp = pygame.transform.scale(self.pfp, (120, 120))

        # LOAD ALL FONTS
        pygame.font.init()
        self.big_font = pygame.font.Font(heav_font, 50)
        self.small_font = pygame.font.Font(chrono_font, 32)
        self.smaller_font = pygame.font.Font(pixel_font, 21)
        self.smallest_font = pygame.font.Font(pixel_font, 16)

        self.maps: List[str] = [
            str(f) for f in Path("maps").rglob("*") if str(f).endswith(".txt")
        ]

        # USEFUL VALUES
        self.customs = False
        self.hue = 0.0
        self.m_pos = pygame.Vector2(150, 260)
        self.i = 0
        self.n_maps = len(self.maps)
        if self.n_maps > 0:
            self.current_map = self.maps[0]
        else:
            self.current_map = ""
        self.chosen_quote = quotes[random.randint(0, len(quotes) - 1)]

    def create_star(
        self, points: int, cx: float, cy: float,
        outer_radius: int, inner_radius: int,
        inner: bool, rot: float
    ) -> List:
        """
        THIS IS THE BEST FUNCTION TO EVER EXIST. CREDIT TO IHSSANE
        -> Create a bunch of vertices in a circle, which when draw in a
        polygon make up a star with however many points specified, this
        is also used for drawing hexagons/pentagons and such...

        cx, cy : position
        outer_radius, inner_radius : star/polygon radius
        inner : if True draws a star in mind
        rot : rotation offset
        """
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

    def run(self) -> str:
        while self.running:
            for event in pygame.event.get():
                # EVENT FOR EDNING PROGRAM DUHH
                if event.type == pygame.QUIT:
                    self.running = False

                # ALL KEY EVENTS
                elif event.type == pygame.KEYDOWN:
                    # GO DOWN IN MAP SELECTION
                    if event.key == pygame.K_DOWN and self.n_maps > 0:
                        self.m_pos += pygame.Vector2(20, 0)
                        self.select_sound.play()
                        self.i = (self.i + 1) % self.n_maps

                    # GO UHP IN MAP SELECTIONNNE
                    if event.key == pygame.K_UP and self.n_maps > 0:
                        self.m_pos += pygame.Vector2(20, 0)
                        self.select_sound.play()
                        self.i = (self.i - 1) % self.n_maps

                    if event.key == pygame.K_c:
                        if not self.customs:
                            self.maps = [
                                str(file)
                                for file in Path("customs").rglob("*")
                                if str(file).endswith(".txt")
                            ]
                            self.n_maps = len(self.maps)
                            self.i = 0
                            self.customs = True
                        else:
                            self.maps = [
                                str(file)
                                for file in Path("maps").rglob("*")
                                if str(file).endswith(".txt")
                            ]
                            self.n_maps = len(self.maps)
                            self.i = 0
                            self.customs = False

                    if self.n_maps > 0:
                        self.current_map = self.maps[self.i]

                    # SELECT MAP
                    if event.key == pygame.K_RETURN:
                        if self.n_maps == 0:
                            return ""
                        pygame.mixer.music.fadeout(300)
                        self.enter_sound.play()
                        self.enter_sound.set_volume(0.1)
                        time.sleep(0.3)
                        return self.current_map

                    # SWITCH TO STORY MODE
                    if event.key == pygame.K_s:
                        manoria()

                    # LEAVE
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return ""

            # RENDER BACKGROUND IMAGE
            self.screen.blit(self.img, (0, 0))

            # ADD IN HUE (THIS COMES IN HANDY LATER TRUST)
            self.hue += 0.01

            # THIS IS FOR WHEN EPOCH FLIES FROM UP TO DOWN
            y = loop_y(time.time(), self.screen.get_height(), speed=0.05)
            self.screen.blit(self.epoch, (800, y - 200))

            self.screen.blit(self.pfp, (25, 380))

            # THIS IS FOR HEADER
            header = self.big_font.render("WELCOME TO FLY-IN", True, "black")
            header_sh = self.big_font.render(
                "WELCOME TO FLY-IN", True, (100, 120, 150))
            header_hs = self.big_font.render(
                "WELCOME TO FLY-IN", True, (5, 5, 8), "lightblue2"
            )

            if self.n_maps != 0:
                choose = self.small_font.render(
                    "// CHOOSE YOUR MAP", True, (10, 10, 12), "lightblue2"
                )
                mapping: List[str] = self.current_map.split("/")
                map_name = mapping[-1][:-4].replace("_", " ").upper()
                difficulty: str = mapping[-2]

                r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)

                diff_colors: dict[str, Color] = {
                    "RIDA SBA3": "black",
                    "ISHMAEL": "magenta",
                    "NIGGER": "brown",
                    "SONIC": "blue",
                    "EASY": "green3",
                    "MEDIUM": "orange",
                    "HARD": "crimson",
                    "CHALLENGER": (int(r * 255), int(g * 255), int(b * 255)),
                }

                color: Color = "grey"

                if difficulty.upper() in diff_colors.keys():
                    color = diff_colors[difficulty.upper()]

                diff = self.big_font.render(difficulty, True, "black", color)
                diff_shadow = self.big_font.render(difficulty, True, "white")

                map_txt = self.big_font.render(
                    map_name,
                    True,
                    (0, 0, 0),
                    "lightblue2",
                )

                n_map = self.small_font.render(
                    self.maps[(self.i + 1) % self.n_maps][:-4]
                    .replace("_", " ")
                    .upper(),
                    True,
                    (0, 0, 0),
                )

                nn_map = self.smaller_font.render(
                    self.maps[(self.i + 2) % self.n_maps][:-4]
                    .replace("_", " ")
                    .upper(),
                    True,
                    (0, 0, 0),
                )

                self.m_pos = self.m_pos.lerp((150, 270), 0.2)

                star3 = self.create_star(
                    8, self.m_pos.x - 100, 280, 120, 105, True, self.hue
                )
                star4 = self.create_star(
                    8, self.m_pos.x - 80, 255, 50, 40, True, self.hue
                )
                pygame.draw.polygon(self.screen, "lightblue2", star3, 0)
                pygame.draw.polygon(self.screen, "black", star3, 5)
                pygame.draw.polygon(self.screen, color, star4, 0)

                n_map.set_alpha(100)
                nn_map.set_alpha(70)

                self.screen.blit(choose, (50, 180))
                self.screen.blit(map_txt, self.m_pos)
                self.screen.blit(diff, self.m_pos + (-100, -38))
                self.screen.blit(diff_shadow, self.m_pos + (-100, -35))
                self.screen.blit(n_map, (130, 320))
                self.screen.blit(nn_map, (125, 350))
            else:
                nomaps_txt = self.big_font.render(
                    "NO MAPS FOUND", False, "black", "lightblue2"
                )
                helper_txt = self.small_font.render(
                    "put any maps you have in the maps/ folder.",
                    False,
                    "black",
                    "lightblue2",
                )

                self.screen.blit(nomaps_txt, (100, 200))
                self.screen.blit(helper_txt, (100, 250))

            star = self.create_star(
                8,
                70,
                60 + math.sin(time.time() * 3 - 0.5) * 8,
                120,
                60,
                True,
                self.hue,
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

            pygame.draw.polygon(self.screen, "black", star, 2)
            pygame.draw.polygon(self.screen, "lightblue2", star2, 0)

            self.screen.blit(
                header_hs, (50, 50 + math.sin(time.time() * 3 - 0.5) * 8))
            self.screen.blit(
                header_sh, (50, 50 + math.sin(time.time() * 3 - 0.2) * 8))
            self.screen.blit(
                header, (50, 50 + math.sin(time.time() * 3) * 8))

            quote = self.smaller_font.render(
                " " + self.chosen_quote + " ", True, (10, 10, 12)
            )
            credit = self.small_font.render("B//", True, (10, 10, 12))

            keys_story = self.smaller_font.render(
                "[ S ] -> Story", True, (200, 200, 220)
            )
            keys_quit = self.smaller_font.render(
                "[ Q ] -> Quit", True, (200, 200, 220))

            pygame.draw.rect(
                self.screen, (200, 200, 240), (650, 40, 125, 55), 0, 5)
            pygame.draw.rect(self.screen, (5, 5, 15), (650, 35, 125, 55), 0, 5)

            self.screen.blit(keys_story, (665, 45))
            self.screen.blit(keys_quit, (665, 65))

            self.screen.blit(quote, (50, 100))
            self.screen.blit(credit, (150, 450))

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        return ""
