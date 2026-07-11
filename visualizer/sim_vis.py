import colorsys
import math
import time
import pygame
from typing import Dict, List


def get_map_rect(SCALE: int, Y_SCALE: int, X_SCALE: int, info: Dict) -> tuple:
    X = max(nfo["x"] for nfo in info["hubs"].values())
    Y = max(nfo["y"] for nfo in info["hubs"].values())
    return ((X * (SCALE + X_SCALE)) + SCALE, (Y * (SCALE + Y_SCALE)) + SCALE)


def get_hub_drones(hub_name: str, turn: str) -> int:
    return len([n for n in turn.split(" ") if n.split("-")[1] == hub_name])


def hue_to_rgb(hue: float) -> tuple:
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return int(r * 255), int(g * 255), int(b * 255)


class SimVis:
    def __init__(self, info: Dict, turns: List) -> None:
        self.info = info
        self.turns = turns
        self.show_info = False
        self.drone_positions: Dict = {}
        self.drone_colors = [
            pygame.Color(255, 75, 75), pygame.Color(255, 165, 0),
            pygame.Color(255, 220, 0), pygame.Color(120, 255, 120),
            pygame.Color(0, 200, 120), pygame.Color(0, 220, 255),
            pygame.Color(0, 140, 255), pygame.Color(80, 80, 255),
            pygame.Color(150, 80, 255), pygame.Color(255, 80, 255),
            pygame.Color(255, 120, 180), pygame.Color(255, 140, 90),
            pygame.Color(180, 255, 120), pygame.Color(120, 255, 200),
            pygame.Color(90, 200, 255), pygame.Color(255, 210, 120),
            pygame.Color(200, 200, 255), pygame.Color(255, 180, 220),
            pygame.Color(160, 255, 160), pygame.Color(255, 255, 255),
            pygame.Color(200, 120, 255), pygame.Color(255, 100, 100),
            pygame.Color(100, 255, 255), pygame.Color(255, 200, 0),
            pygame.Color(180, 180, 180),
        ]

        self.hue = 0.0
        self.SCALE = 100
        self.Y_SCALE = 10
        self.X_SCALE = 20
        self.SCREEN_X = 1600
        self.SCREEN_Y = 900

        pygame.mixer.init()
        pygame.mixer.music.load("sounds/sim.mp3")
        pygame.mixer.music.play()

        self._fit_scale_to_screen()

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.SCREEN_X, self.SCREEN_Y), pygame.SRCALPHA
        )
        self.info_layer = pygame.Surface(
            (self.SCREEN_X, self.SCREEN_Y), pygame.SRCALPHA
        )
        self.clock = pygame.time.Clock()
        self.running = True

        self.img = pygame.image.load("images/crono.jpg").convert()
        self.img = pygame.transform.scale(self.img, self.screen.get_size())
        self.img.set_alpha(255)

        self.epoch_sound = pygame.mixer.Sound("sounds/woosh.wav")
        self.epoch_sound.set_volume(0.4)

        pygame.font.init()

        self.offset = pygame.Vector2(0, 0)
        self.zoom_offset = pygame.Vector2(0, 0)

        self.center_pos = pygame.Vector2(
            self.SCREEN_X // 2 - self.map_rect[0] // 2 + self.SCALE // 3,
            self.SCREEN_Y // 2 - self.map_rect[1] // 2 + self.SCALE,
        )

        self.my_font = pygame.font.Font("fonts/Pixeltype.ttf", 25)
        self.big_font = pygame.font.Font("fonts/ChronoType.ttf", 48)

        self.turn = 0

        # raw sprites, rescaled per-frame based on current SCALE
        self.raw_epoch = pygame.image.load("images/epoch.png")
        self.raw_blackbird = pygame.image.load("images/blackbird.gif")
        self.raw_dorino = pygame.image.load("images/Dorino.gif")
        self.raw_medina = pygame.image.load("images/Medina.gif")
        self.raw_peak = pygame.image.load("images/peak.gif")
        self.raw_meteor = pygame.image.load("images/meteor.gif")

    def _fit_scale_to_screen(self) -> None:
        self.map_rect = get_map_rect(
            self.SCALE, self.Y_SCALE, self.X_SCALE, self.info
        )

        while self.map_rect[0] > self.SCREEN_X - 100:
            self.SCALE -= 5
            self.map_rect = get_map_rect(
                self.SCALE, self.Y_SCALE, self.X_SCALE, self.info
            )

        while self.map_rect[1] > self.SCREEN_Y - 100:
            self.SCALE -= 5
            self.Y_SCALE -= 1
            self.map_rect = get_map_rect(
                self.SCALE, self.Y_SCALE, self.X_SCALE, self.info
            )

        self.SCALE = max(self.SCALE, 30)

    def create_star(
        self, points: int, cx: float, cy: float,
        outer_radius: int, inner_radius: int, inner: bool, rot: float
    ) -> List:
        if points < 2:
            points, inner_radius = 10, outer_radius

        n = points * 2 if inner else points
        step = math.pi / points if inner else 2 * math.pi / points
        vertices = []
        for idx in range(n):
            angle = math.pi / 2 + idx * step
            if inner:
                radius = outer_radius if idx % 2 == 0 else inner_radius
            else:
                radius = outer_radius
            x = cx + math.cos(angle + rot) * radius
            y = cy - math.sin(angle + rot) * radius
            vertices.append((x, y))
        return vertices

    def _rescale_sprites(self) -> None:
        s = self.SCALE
        self.epoch = pygame.transform.rotate(
            pygame.transform.scale(self.raw_epoch, (s // 2, s // 2)), 90
        )
        self.blackbird = pygame.transform.rotate(
            pygame.transform.scale(
                self.raw_blackbird, (s // 1.7, s // 1.7)
            ),
            -90,
        )
        self.dorino = pygame.transform.scale(self.raw_dorino, (s, s))
        self.medina = pygame.transform.scale(self.raw_medina, (s, s))
        self.peak = pygame.transform.scale(
            self.raw_peak, (s // 1.5, s // 1.5)
        )
        self.meteor = pygame.transform.scale(self.raw_meteor, (s, s))

    def handle_keydown(self, key: int) -> None:
        if key in (pygame.K_q, pygame.K_ESCAPE):
            self.running = False

        if key == pygame.K_RIGHT and self.turn + 1 <= len(self.turns) - 1:
            self.turn += 1
            self.epoch_sound.play()

        if key == pygame.K_LEFT and self.turn - 1 >= 0:
            self.turn -= 1
            self.epoch_sound.play()

        if key == pygame.K_r:
            self.zoom_offset.x = 0
            self.zoom_offset.y = 0
            self.turn = 0
            self.epoch_sound.play()

        if key == pygame.K_f:
            self.show_info = not self.show_info

        if key == pygame.K_m:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()

    def update_camera(self) -> None:
        keys = pygame.key.get_pressed()

        # live camera pan
        if keys[pygame.K_d]:
            self.zoom_offset.x -= 10
        if keys[pygame.K_a]:
            self.zoom_offset.x += 10
        if keys[pygame.K_w]:
            self.zoom_offset.y += 10
        if keys[pygame.K_s]:
            self.zoom_offset.y -= 10

        # live zoom
        if keys[pygame.K_c] and self.SCALE < 300:
            self.SCALE += 4
        if keys[pygame.K_x] and self.SCALE > 50:
            self.SCALE -= 4

    def hub_screen_pos(self, nfo: Dict) -> pygame.Vector2:
        x = self.center_pos.x + (nfo["x"] * (self.SCALE + self.X_SCALE))
        y = self.center_pos.y + (nfo["y"] * (self.SCALE + self.Y_SCALE))
        return pygame.Vector2(x, y) + self.zoom_offset + self.offset

    def draw_connections(self) -> None:
        for cn1, cn2, max_link in self.info["connections"]:
            start_pos = self.hub_screen_pos(self.info["hubs"][cn1])
            end_pos = self.hub_screen_pos(self.info["hubs"][cn2])
            center_coords = (
                (start_pos.x + end_pos.x) / 2,
                (start_pos.y + end_pos.y) / 2,
            )

            pygame.draw.line(
                self.screen, "chocolate4", start_pos,
                end_pos, self.SCALE // 14 + 5
            )
            pygame.draw.line(
                self.screen, "chocolate3", start_pos,
                end_pos, self.SCALE // 14
            )

            if self.show_info:
                conn_txt = self.my_font.render(
                    "max:" + str(max_link), False, "lightblue2", "black"
                )
                self.info_layer.blit(conn_txt, center_coords)

    def draw_hub_terrain(self, pos: pygame.Vector2) -> None:
        dirt = self.create_star(
            8, pos.x, pos.y + 8, self.SCALE // 3, 0, False, 0
        )
        grass = self.create_star(8, pos.x, pos.y, self.SCALE // 3, 0, False, 0)
        grass2 = self.create_star(
            8, pos.x, pos.y, self.SCALE // 5, 0, False, 0)
        mount = self.create_star(8, pos.x, pos.y, self.SCALE // 8, 0, False, 0)

        pygame.draw.polygon(self.screen, "coral4", dirt)
        pygame.draw.polygon(self.screen, "darkgreen", grass)
        pygame.draw.polygon(self.screen, "green4", grass2)
        pygame.draw.polygon(self.screen, "coral4", mount)

    def draw_hub_sprite(self, pos: pygame.Vector2, zone: str) -> None:
        s = self.SCALE
        sprites = {
            "normal": (self.dorino, (s // 2, s // 2)),
            "priority": (self.medina, (s // 2 - 4, s // 2)),
            "restricted": (self.peak, (s // 3, s // 1.7)),
            "blocked": (self.meteor, (s // 2, s // 2)),
        }
        if zone in sprites:
            sprite, (dx, dy) = sprites[zone]
            self.screen.blit(sprite, pos - pygame.Vector2(dx, dy))

    def draw_hubs(self) -> None:
        for hub, nfo in self.info["hubs"].items():
            pos = self.hub_screen_pos(nfo)
            drones = get_hub_drones(hub, self.turns[self.turn])
            color = nfo["color"]
            zone = nfo["zone"]

            self.draw_hub_terrain(pos)

            if color == "rainbow":
                color = hue_to_rgb(self.hue)

            self.draw_hub_sprite(pos, zone)

            star = self.create_star(
                drones, pos.x, pos.y, self.SCALE // 15,
                self.SCALE // 5, True, self.hue,
            )
            pygame.draw.polygon(self.screen, color, star)

            if self.show_info:
                label = hub + "[" + zone[0].upper()
                label += str(nfo["max_drones"]) + "]"
                zone_txt = self.my_font.render(
                    label, True, "lightblue2", "black"
                )
                self.info_layer.blit(
                    zone_txt, pos + pygame.Vector2(-20, self.SCALE // 2 - 10)
                )

    def drone_hub_center(self, parts: List[str]) -> pygame.Vector2:
        hub_a = self.info["hubs"][parts[1]]
        if len(parts) == 3:
            hub_b = self.info["hubs"][parts[2]]
            hx = (hub_a["x"] + hub_b["x"]) / 2
            hy = (hub_a["y"] + hub_b["y"]) / 2
        else:
            hx, hy = hub_a["x"], hub_a["y"]

        return pygame.Vector2(
            self.center_pos.x + hx * (self.SCALE + self.X_SCALE)
            + self.zoom_offset.x,
            self.center_pos.y + hy * (self.SCALE + self.Y_SCALE)
            + self.zoom_offset.y,
        ) + self.offset

    def draw_drones(self) -> None:
        drone_info = self.turns[self.turn].split(" ")

        for drone_pos in drone_info:
            parts = drone_pos.split("-")
            drone, drone_hub = parts[0], self.info["hubs"][parts[1]]
            drone_num = int(drone.strip("D"))
            hub_center = self.drone_hub_center(parts)

            positions = self.create_star(
                len(drone_info),
                hub_center.x - (self.SCALE // 4),
                hub_center.y - (self.SCALE // 4),
                self.SCALE // 2, 0, False, self.hue,
            )
            target_pos = pygame.Vector2(positions[drone_num - 1])

            if drone not in self.drone_positions:
                self.drone_positions[drone] = target_pos

            self.drone_positions[drone] = (
                self.drone_positions[drone].lerp(target_pos, 0.4)
            )

            line_color = drone_hub["color"]
            if line_color == "rainbow":
                line_color = hue_to_rgb(self.hue)

            pygame.draw.line(
                self.screen, line_color, hub_center,
                target_pos + (self.SCALE // 4, self.SCALE // 4), 2,
            )

            ship = self.blackbird if drone_num % 2 == 0 else self.epoch
            self.screen.blit(ship, self.drone_positions[drone])

            if self.show_info:
                drone_text = self.my_font.render(
                    drone + " [" + str(drone_hub["name"]) + "]",
                    False, "lightblue2", "black",
                )
                self.info_layer.blit(drone_text, target_pos)

    def draw_ui(self) -> None:
        title = self.big_font.render(
            self.info["map_path"].split("/")[-1].upper(),
            True, (255, 255, 255)
        )
        turns_txt = self.my_font.render(
            "turn : " + str(self.turn) + "/" + str(len(self.turns) - 1),
            True, (255, 255, 255),
        )
        max_drones = self.my_font.render(
            "Number of Drones : " + str(self.info["nb_drones"]),
            True, (150, 150, 180),
        )

        self.screen.blit(title, (50, 50))
        self.screen.blit(turns_txt, (50, 80))
        self.screen.blit(max_drones, (50, 150))
        self.screen.blit(self.info_layer, (0, 0))

        menu_texts = [
            "[ > ] - NEXT TURN",
            "[ < ] - PREVIOUS TURN",
            "[ C ] - ZOOM IN",
            "[ X ] - ZOOM OUT",
            "[ WASD ] - MOVE CAMERA",
            "[ F ] - DISPLAY INFORMATION",
            "[ R ] - RESET SIMULATION",
        ]
        menu_color = (70, 85, 110)
        start_x = 20
        start_y = self.SCREEN_Y - (len(menu_texts) * 25) - 20

        for i, text in enumerate(menu_texts):
            txt_surface = self.my_font.render(text, True, menu_color)
            self.screen.blit(txt_surface, (start_x, start_y + i * 25))

    def render_frame(self) -> None:
        self.screen.blit(self.img, (0, 0) + self.zoom_offset // 40)

        self.offset = pygame.Vector2(
            math.cos(time.time()) * 10, math.sin(time.time()) * 10
        )
        self.hue += 0.01

        self.update_camera()
        self._rescale_sprites()

        self.info_layer.fill((0, 0, 0, 0))

        self.draw_connections()
        self.draw_hubs()
        self.draw_drones()
        self.draw_ui()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

            self.render_frame()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
