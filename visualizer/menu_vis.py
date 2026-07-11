import colorsys
import math
import random
import time
from pathlib import Path
from typing import List, Union

import pygame as pg

from visualizer.manoria_vis import Menoria

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

DIFF_COLORS: dict[str, Color] = {
    "RIDA SBA3": "black",
    "ISHMAEL": "magenta",
    "SONIC": "blue",
    "EASY": "green3",
    "MEDIUM": "orange",
    "HARD": "crimson",
}


def loop_y(t: float, screen_h: int, speed: float) -> float:
    return (t * speed * screen_h) % (screen_h + 500)


def load_maps(folder: str) -> List[str]:
    return [str(f) for f in Path(folder).rglob("*") if str(f).endswith(".txt")]


class MenuViz:
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()

        self.SCREEN_X, self.SCREEN_Y = 1000, 500
        self.screen = pg.display.set_mode((self.SCREEN_X, self.SCREEN_Y))
        self.clock = pg.time.Clock()
        self.running = True

        pg.display.set_caption("Fly-In Trigger")
        pg.display.set_icon(pg.image.load("images/chronoIcon.png"))

        pg.mixer.music.load("sounds/menu.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_pos(0.5)

        self.select_sound = pg.mixer.Sound("sounds/blipSelect.wav")
        self.enter_sound = pg.mixer.Sound("sounds/Enter.wav")
        self.select_sound.set_volume(0.2)
        self.enter_sound.set_volume(0.4)

        self.img = pg.transform.scale(
            pg.image.load("images/crono.jpg").convert(),
            self.screen.get_size()
        )
        self.epoch = pg.image.load("images/epoch.png")
        self.epoch = pg.transform.scale(self.epoch, (120, 100))
        self.epoch.set_alpha(200)
        self.pfp = pg.image.load("images/pfp.png")
        self.pfp = pg.transform.scale(self.pfp, (120, 120))

        pg.font.init()
        self.big_font = pg.font.Font(heav_font, 50)
        self.small_font = pg.font.Font(chrono_font, 32)
        self.smaller_font = pg.font.Font(pixel_font, 21)
        self.smallest_font = pg.font.Font(pixel_font, 16)

        self.customs = False
        self.hue = 0.0
        self.m_pos = pg.Vector2(150, 260)
        self.i = 0
        self.maps = load_maps("maps")
        self.n_maps = len(self.maps)
        self.current_map = self.maps[0] if self.n_maps else ""
        self.chosen_quote = random.choice(quotes)

    def create_star(
        self, points: int, cx: float, cy: float,
        outer_radius: int, inner_radius: int,
        inner: bool, rot: float
    ) -> List:

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

    def toggle_customs(self) -> None:
        self.customs = not self.customs
        self.maps = load_maps("customs" if self.customs else "maps")
        self.n_maps = len(self.maps)
        self.i = 0

    def get_diff_color(self, difficulty: str) -> Color:
        if difficulty.upper() == "CHALLENGER":
            r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
            return int(r * 255), int(g * 255), int(b * 255)
        return DIFF_COLORS.get(difficulty.upper(), "grey")

    def handle_keydown(self, key: int) -> Union[str, None]:
        if key in (pg.K_DOWN, pg.K_UP) and self.n_maps > 0:
            self.m_pos += pg.Vector2(20, 0)
            self.select_sound.play()
            self.i = (self.i + (1 if key == pg.K_DOWN else -1)) % self.n_maps

        if key == pg.K_c:
            self.toggle_customs()

        if self.n_maps > 0:
            self.current_map = self.maps[self.i]

        if key == pg.K_RETURN:
            if self.n_maps == 0:
                return ""
            pg.mixer.music.fadeout(300)
            self.enter_sound.play()
            self.enter_sound.set_volume(0.1)
            time.sleep(0.3)
            return self.current_map

        if key == pg.K_s:
            m = Menoria("images/story.jpg", "sounds/manoria.mp3")
            m.run()

        if key in (pg.K_q, pg.K_ESCAPE):
            return ""

        return None

    def render_map_selector(self) -> None:
        choose = self.small_font.render("// CHOOSE YOUR MAP", True,
                                        (10, 10, 12), "lightblue2")
        mapping = self.current_map.split("/")
        map_name = mapping[-1][:-4].replace("_", " ").upper()
        difficulty = mapping[-2]
        color = self.get_diff_color(difficulty)

        diff = self.big_font.render(difficulty, True, "black", color)
        diff_shadow = self.big_font.render(difficulty, True, "white")
        map_txt = self.big_font.render(map_name, True, (0, 0, 0), "lightblue2")

        n_map = self.small_font.render(
            self.maps[(self.i + 1) % self.n_maps][:-4].replace("_", " "),
            True, (0, 0, 0)
        )
        nn_map = self.smaller_font.render(
            self.maps[(self.i + 2) % self.n_maps][:-4].replace("_", " "),
            True, (0, 0, 0)
        )

        self.m_pos = self.m_pos.lerp((150, 270), 0.2)

        star3 = self.create_star(
            8, self.m_pos.x - 100, 280, 120, 105, True, self.hue)
        star4 = self.create_star(
            8, self.m_pos.x - 80, 255, 50, 40, True, self.hue)
        pg.draw.polygon(self.screen, "lightblue2", star3, 0)
        pg.draw.polygon(self.screen, "black", star3, 5)
        pg.draw.polygon(self.screen, color, star4, 0)

        n_map.set_alpha(100)
        nn_map.set_alpha(70)

        self.screen.blit(choose, (50, 180))
        self.screen.blit(map_txt, self.m_pos)
        self.screen.blit(diff, self.m_pos + (-100, -38))
        self.screen.blit(diff_shadow, self.m_pos + (-100, -35))
        self.screen.blit(n_map, (130, 320))
        self.screen.blit(nn_map, (125, 350))

    def render_no_maps(self) -> None:
        self.screen.blit(
            self.big_font.render(
                "NO MAPS FOUND", False, "black", "lightblue2"), (100, 200)
        )
        self.screen.blit(
            self.small_font.render(
                "put any maps you have in the maps/ folder.", False, "black",
                "lightblue2"
            ),
            (100, 250),
        )

    def render_frame(self) -> None:
        self.screen.blit(self.img, (0, 0))
        self.hue += 0.01

        y = loop_y(time.time(), self.screen.get_height(), speed=0.05)
        self.screen.blit(self.epoch, (800, y - 200))
        self.screen.blit(self.pfp, (25, 380))

        wobble = math.sin(time.time() * 3 - 0.5) * 8
        header = self.big_font.render(
            "WELCOME TO FLY-IN", True, (200, 200, 220))
        header_sh = self.big_font.render(
            "WELCOME TO FLY-IN", True, (100, 120, 150))
        header_hs = self.big_font.render(
            "WELCOME TO FLY-IN", True, (5, 5, 8))

        if self.n_maps != 0:
            self.render_map_selector()
        else:
            self.render_no_maps()

        self.screen.blit(header_hs, (50, 30 + wobble))
        self.screen.blit(header_sh, (
            50, 30 + math.sin(time.time() * 3 - 0.2) * 8))
        self.screen.blit(header, (50, 30 + math.sin(time.time() * 3) * 8))

        quote = self.smaller_font.render(
            f" {self.chosen_quote} ", True, (10, 10, 12))
        credit = self.small_font.render("B//", True, (10, 10, 12))
        keys_story = self.smaller_font.render(
            "[ C ] -> Customs", True, (200, 200, 220))
        keys_quit = self.smaller_font.render(
            "[ Q ] -> Quit", True, (200, 200, 220))

        self.screen.blit(keys_story, (self.SCREEN_X - 130, 45))
        self.screen.blit(keys_quit, (self.SCREEN_X - 130, 65))
        self.screen.blit(quote, (50, 100))
        self.screen.blit(credit, (150, 450))

    def run(self) -> str:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    result = self.handle_keydown(event.key)
                    if result is not None:
                        return result

            self.render_frame()
            pg.display.flip()
            self.clock.tick(30)

        pg.quit()
        return ""
