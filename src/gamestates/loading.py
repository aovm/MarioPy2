import gamestates.gamestate as gs
import pygame
import constants as c

class Loading(gs.GameState):

    def __init__(self, game) -> None:
        super().__init__(game)
        self.mIcon = self.game.res['UI']['mario_icon']
        self.cIcon = self.game.res['UI']['coin_icon']
        self.xIcon = self.game.res['UI']['x']
        self.ctime = 0.0
    
    def assignData(self, nextState): 
        self.next: gs.GameState = nextState

    def update(self, dt, keys):
        super().update(dt, keys)
        self.ctime += dt
        if self.ctime > c.LOADING_TIME:
            self.ctime = 0.0
            self.marioLives = 0
            self.next.start()
            self.game.currentState = self.next
            self.next = None

    def render(self, screen: pygame.Surface):
        super().render(screen)
        screen.fill(c.BLACK)

        self.game.drawUIText("Mario", (60, 23))
        self.game.drawUIText(f"{self.game.totalScore : 07d}", (40, 42))

        self.game.drawUIText("World", (350, 23))
        self.game.drawUIText(self.next.title, (370, 42))

        self.game.drawUIText("Time", (490, 23)) 

        self.game.drawUIIcon(self.xIcon, (240, 41))
        self.game.drawUIIcon(self.cIcon, (220, 36))
        self.game.drawUIText("00", (260, 36))

        self.game.drawUIText("ALPHA", (60, 66))
        self.game.drawUIText(f"World {self.next.title}", (217, 180))
        self.game.drawUIIcon(self.xIcon, (310, 255))
        self.game.drawUIIcon(self.mIcon, (255, 240))
        self.game.drawUIText(str(self.game.marioLives), (340, 249))

