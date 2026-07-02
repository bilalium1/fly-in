import colorsys
import math
import time

import pygame


def get_map_rect(SCALE, Y_SCALE, X_SCALE, info):
    X = max([nfo["x"] for h, nfo in info["hubs"].items()])
    Y = max([nfo["y"] for h, nfo in info["hubs"].items()])
    return ((X * (SCALE + X_SCALE)) + SCALE, (Y * (SCALE + Y_SCALE)) + SCALE)


def get_hub_drones(hub_name, turn):
    x = [n for n in turn.split(" ") if n.split("-")[1] == hub_name]
    return len(x)


class SimVis:
    def __init__(self, info, turns):
        self.info = info
        self.turns = turns
        self.show_info = False
        self.drone_positions = {}
        self.drone_colors = [
            pygame.Color(255, 75, 75),  # red
            pygame.Color(255, 165, 0),  # orange
            pygame.Color(255, 220, 0),  # yellow
            pygame.Color(120, 255, 120),  # green
            pygame.Color(0, 200, 120),  # teal green
            pygame.Color(0, 220, 255),  # cyan
            pygame.Color(0, 140, 255),  # blue
            pygame.Color(80, 80, 255),  # deep blue
            pygame.Color(150, 80, 255),  # purple
            pygame.Color(255, 80, 255),  # magenta
            pygame.Color(255, 120, 180),  # pink
            pygame.Color(255, 140, 90),  # salmon
            pygame.Color(180, 255, 120),  # lime
            pygame.Color(120, 255, 200),  # mint
            pygame.Color(90, 200, 255),  # sky blue
            pygame.Color(255, 210, 120),  # sand
            pygame.Color(200, 200, 255),  # light blue
            pygame.Color(255, 180, 220),  # light pink
            pygame.Color(160, 255, 160),  # light green
            pygame.Color(255, 255, 255),  # white (accent drones)
            pygame.Color(200, 120, 255),  # violet
            pygame.Color(255, 100, 100),  # strong red
            pygame.Color(100, 255, 255),  # bright cyan
            pygame.Color(255, 200, 0),  # gold
            pygame.Color(180, 180, 180),  # gray
        ]

        self.hue = 0

        self.SCALE = 100
        self.Y_SCALE = 10
        self.X_SCALE = 20

        self.SCREEN_X = 1600
        self.SCREEN_Y = 900

        pygame.mixer.init()
        pygame.mixer.music.load("sounds/sim.mp3")
        pygame.mixer.music.play()

        self.map_rect = get_map_rect(self.SCALE, self.Y_SCALE, self.X_SCALE, self.info)

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

        if self.SCALE < 30:
            self.SCALE = 30

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
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.running = False

                    if (
                        event.key == pygame.K_RIGHT
                        and self.turn + 1 <= len(self.turns) - 1
                    ):
                        self.turn += 1
                        self.epoch_sound.play()

                    if event.key == pygame.K_LEFT and self.turn - 1 >= 0:
                        self.turn -= 1
                        self.epoch_sound.play()

                    if event.key == pygame.K_r:
                        self.turn = 0
                        self.epoch_sound.play()

                    if event.key == pygame.K_f:
                        self.show_info = not self.show_info

                    if event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()

            self.screen.blit(self.img, (0, 0) + self.zoom_offset // 40)

            self.offset = pygame.Vector2(
                math.cos(time.time()) * 10, math.sin(time.time()) * 10
            )

            self.hue += 0.01

            keys = pygame.key.get_pressed()

            # LIVE MAP MOVING MY NIGGA
            if keys[pygame.K_d]:
                self.zoom_offset.x -= 10
            if keys[pygame.K_a]:
                self.zoom_offset.x += 10
            if keys[pygame.K_w]:
                self.zoom_offset.y += 10
            if keys[pygame.K_s]:
                self.zoom_offset.y -= 10

            # LIVE ZOOM MY NIGGA
            if keys[pygame.K_c] and self.SCALE < 300:
                self.SCALE += 4
            if keys[pygame.K_x] and self.SCALE > 50:
                self.SCALE -= 4

            self.epoch = pygame.image.load("images/epoch.png")
            self.epoch = pygame.transform.scale(
                self.epoch, (self.SCALE // 2, self.SCALE // 2)
            )
            self.epoch = pygame.transform.rotate(self.epoch, 90)

            self.blackbird = pygame.image.load("images/blackbird.gif")
            self.blackbird = pygame.transform.scale(
                self.blackbird, (self.SCALE // 1.7, self.SCALE // 1.7)
            )
            self.blackbird = pygame.transform.rotate(self.blackbird, -90)

            self.dorino = pygame.image.load("images/Dorino.gif")
            self.dorino = pygame.transform.scale(self.dorino, (self.SCALE, self.SCALE))

            self.medina = pygame.image.load("images/Medina.gif")
            self.medina = pygame.transform.scale(self.medina, (self.SCALE, self.SCALE))

            self.peak = pygame.image.load("images/peak.gif")
            self.peak = pygame.transform.scale(
                self.peak, (self.SCALE // 1.5, self.SCALE // 1.5)
            )

            self.meteor = pygame.image.load("images/meteor.gif")
            self.meteor = pygame.transform.scale(self.meteor, (self.SCALE, self.SCALE))

            self.plat = pygame.image.load("images/plat.png")
            self.plat = pygame.transform.scale(self.plat, (self.SCALE, self.SCALE))

            self.info_layer.fill((0, 0, 0, 0))

            # connections
            for cn1, cn2, max_link in self.info["connections"]:
                start_pos = (
                    pygame.Vector2(
                        self.center_pos.x
                        + self.info["hubs"][cn1]["x"] * (self.SCALE + self.X_SCALE),
                        self.center_pos.y
                        + self.info["hubs"][cn1]["y"] * (self.SCALE + self.Y_SCALE),
                    )
                    + self.zoom_offset
                    + self.offset
                )

                end_pos = (
                    pygame.Vector2(
                        self.center_pos.x
                        + self.info["hubs"][cn2]["x"] * (self.SCALE + self.X_SCALE),
                        self.center_pos.y
                        + self.info["hubs"][cn2]["y"] * (self.SCALE + self.Y_SCALE),
                    )
                    + self.zoom_offset
                    + self.offset
                )

                center_coords = (
                    (start_pos.x + end_pos.x) / 2,
                    (start_pos.y + end_pos.y) / 2,
                )

                pygame.draw.line(
                    self.screen, "chocolate4", start_pos, end_pos, self.SCALE // 14 + 5
                )
                pygame.draw.line(
                    self.screen, "chocolate3", start_pos, end_pos, self.SCALE // 14
                )

                conn_txt = self.my_font.render(
                    "max:" + str(max_link), False, "lightblue2", "black"
                )

                if self.show_info:
                    self.info_layer.blit(conn_txt, center_coords)

            # hubs
            for hub, nfo in self.info["hubs"].items():
                x = self.center_pos.x + (nfo["x"] * (self.SCALE + self.X_SCALE))
                y = self.center_pos.y + (nfo["y"] * (self.SCALE + self.Y_SCALE))
                pos = pygame.Vector2(x, y) + self.zoom_offset + self.offset
                drones = get_hub_drones(hub, self.turns[self.turn])

                color = nfo["color"]
                zone = nfo["zone"]
                max_dones = nfo["max_drones"]

                hexagon_dirt = self.create_star(
                    8, pos.x, pos.y + 8, self.SCALE // 3, 0, False, 0
                )
                hexagon_grass = self.create_star(
                    8, pos.x, pos.y, self.SCALE // 3, 0, False, 0
                )
                hexagon_grass2 = self.create_star(
                    8, pos.x, pos.y, self.SCALE // 5, 0, False, 0
                )
                hexagon_mount = self.create_star(
                    8, pos.x, pos.y, self.SCALE // 8, 0, False, 0
                )

                # pygame.draw.circle(
                #    self.screen, "coral4", pos + pygame.Vector2(0, 8), self.SCALE // 3
                # )
                # pygame.draw.circle(self.screen, "darkolivegreen", pos, self.SCALE // 3)
                # pygame.draw.circle(self.screen, "coral4", pos, self.SCALE // 8)

                pygame.draw.polygon(self.screen, "coral4", hexagon_dirt)
                pygame.draw.polygon(self.screen, "darkgreen", hexagon_grass)
                pygame.draw.polygon(self.screen, "green4", hexagon_grass2)
                pygame.draw.polygon(self.screen, "coral4", hexagon_mount)

                # self.screen.blit(self.plat, pos - (self.SCALE // 2, self.SCALE // 2))

                if color == "rainbow":
                    r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
                    color = (int(r * 255), int(g * 255), int(b * 255))

                if zone == "normal":
                    self.screen.blit(
                        self.dorino,
                        pos - pygame.Vector2(self.SCALE // 2, self.SCALE // 2),
                    )
                elif zone == "priority":
                    self.screen.blit(
                        self.medina,
                        pos - pygame.Vector2(self.SCALE // 2 - 4, self.SCALE // 2),
                    )

                elif zone == "restricted":
                    self.screen.blit(
                        self.peak,
                        pos - pygame.Vector2(self.SCALE // 3, self.SCALE // 1.7),
                    )

                elif zone == "blocked":
                    self.screen.blit(
                        self.meteor,
                        pos - pygame.Vector2(self.SCALE // 2, self.SCALE // 2),
                    )

                star = self.create_star(
                    drones,
                    pos.x,
                    pos.y,
                    self.SCALE // 15,
                    self.SCALE // 5,
                    True,
                    self.hue,
                )
                pygame.draw.polygon(self.screen, color, star)

                # text
                zone_name_txt = self.my_font.render(
                    hub + " [" + zone[0].upper() + str(max_dones) + "]",
                    True,
                    "lightblue2",
                    "black",
                )

                # zone_name_txt = pygame.transform.rotate(zone_name_txt, 0)

                if self.show_info:
                    self.info_layer.blit(
                        zone_name_txt, pos + pygame.Vector2(-20, self.SCALE // 2 - 10)
                    )

            # drones
            drone_info = self.turns[self.turn].split(" ")

            for drone_pos in drone_info:
                drone = drone_pos.split("-")[0]
                drone_num = int(drone.strip("D"))
                drone_hub = self.info["hubs"][drone_pos.split("-")[1]]

                if len(drone_pos.split("-")) == 3:
                    drone_neighbor = self.info["hubs"][drone_pos.split("-")[2]]
                    hub_center = (
                        pygame.Vector2(
                            self.center_pos.x
                            + (drone_hub["x"] + drone_neighbor["x"])
                            / 2
                            * (self.SCALE + self.X_SCALE)
                            + self.zoom_offset.x,
                            self.center_pos.y
                            + (drone_hub["y"] + drone_neighbor["y"])
                            / 2
                            * (self.SCALE + self.Y_SCALE)
                            + self.zoom_offset.y,
                        )
                        + self.offset
                    )
                else:
                    hub_center = (
                        pygame.Vector2(
                            self.center_pos.x
                            + drone_hub["x"] * (self.SCALE + self.X_SCALE)
                            + self.zoom_offset.x,
                            self.center_pos.y
                            + drone_hub["y"] * (self.SCALE + self.Y_SCALE)
                            + self.zoom_offset.y,
                        )
                        + self.offset
                    )

                positions = self.create_star(
                    len(drone_info),
                    hub_center.x - (self.SCALE // 4),
                    hub_center.y - (self.SCALE // 4),
                    self.SCALE // 2,
                    0,
                    False,
                    self.hue,
                )

                target_pos = pygame.Vector2(positions[drone_num - 1])

                # First time seeing this drone
                if drone not in self.drone_positions:
                    self.drone_positions[drone] = target_pos

                # Smoothly move toward the target
                self.drone_positions[drone] = self.drone_positions[drone].lerp(
                    target_pos, 0.4
                )

                line_color = drone_hub["color"]
                if line_color == "rainbow":
                    r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
                    line_color = (int(r * 255), int(g * 255), int(b * 255))

                pygame.draw.line(
                    self.screen,
                    line_color,
                    hub_center,
                    target_pos + (self.SCALE // 4, self.SCALE // 4),
                    2,
                )

                if drone_num % 2 == 0:
                    ship = self.blackbird
                else:
                    ship = self.epoch

                self.screen.blit(ship, self.drone_positions[drone])
                drone_text = self.my_font.render(
                    drone + " [" + str(drone_hub["name"]) + "]",
                    False,
                    "lightblue2",
                    "black",
                )

                if self.show_info:
                    self.info_layer.blit(drone_text, target_pos)

            # text
            title = self.big_font.render(
                self.info["map_path"].split("/")[-1].upper(), True, (255, 255, 255)
            )

            turns_txt = self.my_font.render(
                "turn : " + str(self.turn) + "/" + str(len(self.turns) - 1),
                True,
                (255, 255, 255),
            )

            max_drones = self.my_font.render(
                "Number of Drones : " + str(self.info["nb_drones"]),
                True,
                (150, 150, 180),
            )

            self.screen.blit(title, (50, 50))
            self.screen.blit(turns_txt, (50, 80))
            self.screen.blit(max_drones, (50, 150))
            self.screen.blit(self.info_layer, (0, 0))

            # pygame.draw.rect(
            #    self.screen, (200, 200, 240), (50, self.SCREEN_Y - 200, 350, 160), 0, 5
            # )
            # pygame.draw.rect(
            #    self.screen, (80, 80, 100), (50, self.SCREEN_Y - 210, 340, 150), 0, 5
            # )

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
