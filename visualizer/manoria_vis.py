import pygame


class Menoria:
    def __init__(self, gif_path: str, music_path: str) -> None:
        # pygame.init()/mixer.init() are safe to call again even if the
        # host app already called them - they no-op if already running.
        pygame.init()
        pygame.mixer.init()

        # Reuse the caller's existing display window if one is open
        # (e.g. launched mid-menu). Only create a fresh one if this
        # screen is being run completely standalone.
        existing_surface = pygame.display.get_surface()
        if existing_surface is not None:
            self.screen = existing_surface
            self.owns_display = False
        else:
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Thank You")
            self.owns_display = True

        self.SCREEN_X, self.SCREEN_Y = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True

        self.gif = pygame.image.load(gif_path)
        self.gif = pygame.transform.scale(
            self.gif, (self.SCREEN_X, self.SCREEN_Y))

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

        pygame.font.init()
        self.font = pygame.font.Font("fonts/Pixeltype.ttf", 32)

        self.thanks_txt = self.font.render(
            "Thank you for playing.", True, (255, 255, 255)
        )
        self.thanks_pos = (
            self.SCREEN_X // 2 - self.thanks_txt.get_width() // 2,
            self.SCREEN_Y // 2,
        )

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.running = False

            self.screen.blit(self.gif, (0, 0))
            self.screen.blit(self.thanks_txt, self.thanks_pos)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.mixer.music.stop()

        # Only fully shut down pygame if we created the display ourselves.
        # If a parent screen (e.g. the menu) is still using pygame, tearing
        # it down here would break that screen's next render/blit call.
        if self.owns_display:
            pygame.quit()


def manoria(gif_path: str = "images/credits.gif",
            music_path: str = "sounds/credits.mp3") -> None:
    Menoria(gif_path, music_path).run()


if __name__ == "__main__":
    manoria()
