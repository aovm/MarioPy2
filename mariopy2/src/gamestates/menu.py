import gamestates.gamestate as gs
import constants as c
import pygame

# ACTIVE RENDER OF UI IN MENU.

class Menu(gs.GameState):

    def __init__(self, game) -> None:
        super().__init__(game)
        self.bg = self.game.res['menu']
        self.bg = pygame.transform.scale(self.bg, \
                                            (c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        self.mIcon = self.game.res['UI']['mario_icon']
        self.cIcon = self.game.res['UI']['coin_icon']
        self.xIcon = self.game.res['UI']['x']
        self.sIcon = self.game.res['UI']['selector']

        self.returnLock = False

        self.updateUIInterval = 0.5
        self.updateUICounter = 0.0
        self.fps = 0.0

        self.singlePlayer = True

    def update(self, dt, keys):
        super().update(dt, keys)
        self.updateUICounter += dt
        if self.updateUICounter > self.updateUIInterval:
            self.updateUICounter = 0.0
            self.fps = 1 / (dt + 0.0000000001)

        if keys[pygame.K_RETURN]:
            if not self.returnLock:
                self.returnLock = True
                if self.singlePlayer:
                    self.game.nextLevel()
                else:
                    print('Este modo no existe.')
        else:
            self.returnLock = False
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.singlePlayer = False
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.singlePlayer = True
    
    def render(self, screen: pygame.Surface):
        super().render(screen)
        screen.blit(self.bg, (0, 0))

        self.game.drawUIText("Mario", (60, 23))
        self.game.drawUIText(f"{self.game.totalScore : 07d}", (40, 42))

        self.game.drawUIText("World", (350, 23))
        self.game.drawUIText("1-1", (370, 42))

        self.game.drawUIText("Time", (490, 23)) 

        self.game.drawUIIcon(self.xIcon, (240, 41))
        self.game.drawUIIcon(self.cIcon, (220, 36))

        self.game.drawUIText("00", (260, 36))
        self.game.drawUIText("ALPHA", (60, 66))

        self.game.drawUIText("© 2022 Orlando".upper(), (230, 295), scaling=1.1, color=c.ROSE_L)

        self.game.drawUIText(f"record-", (200, 464))
        self.game.drawUIText(f"{self.game.maxScore : 07d}", (340, 464))

        self.game.drawUIText(f"1 jugador", (220, 360))
        self.game.drawUIText(f"2 jugadores", (220, 400))

        if self.singlePlayer:
            self.game.drawUIIcon(self.sIcon, (180, 360))
        else:
            self.game.drawUIIcon(self.sIcon, (180, 400))

        if c.DEBUG_MODE:
            self.game.drawUIText(f"FPS: {self.fps : .2f}", (104, 300), scaling=0.6)
