from entities.kin_object import KinecticObject
from viewport import Viewport
from components.utils import Utils
import constants as c
import pygame

class Bricks(KinecticObject): 

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, c.BRICKS, data)
        self.used = False

        self.containedCoins = -1

        if data == c.STAR:
            self.containsItem = True
        elif data == "coin1":
            self.containedCoins = 1
            self.containsItem = True
        elif data == "coin5":
            self.containedCoins = 5
            self.containsItem = True
        elif data == "coin10":
            self.containedCoins = 10
            self.containsItem = True
        elif data == "coin12":
            self.containedCoins = 12
            self.containsItem = True
        elif data == "coin20000":
            self.containedCoins = 20000
            self.containsItem = True
        else:
            self.containsItem = False

        self.orgPos = pygame.Vector2(self.position.x, self.position.y)

        self.hit_event = False
        self.hit_countdown = 0.0

    def updateTexture(self, game_res: dict) -> pygame.Surface:
        if self.used:
            return game_res['blocks']['?block']['4']
        else:
            return game_res['blocks']['bricks']
            
    def render(self, viewport: Viewport, game_res: dict) -> None:
        super().render(viewport, game_res)
        viewport.mapBlit(self.updateTexture(game_res), (self.position.x, self.position.y))

    def animationHitEvent(self, dt: float):
        self.hit_countdown += dt
        
        indicator = Utils.maprange((0, c.BRICKS_ANIMATION_DURATION), (0, 14), self.hit_countdown)

        if indicator <= 6:
            self.changePosition((self.position.x, self.orgPos.y - indicator))
        elif indicator <= 12:
            g = Utils.maprange((6, 12), (6, 0), indicator)
            self.changePosition((self.position.x, self.orgPos.y - g ))
        elif indicator <= 13:
            g = Utils.maprange((12, 13), (0, 1), indicator)
            self.changePosition((self.position.x, self.orgPos.y + g ))
        elif indicator <= 14:
            g = Utils.maprange((13, 14), (1, 0), indicator)
            self.changePosition((self.position.x, self.orgPos.y + g ))
        else:
            self.changePosition((self.position.x, self.orgPos.y))
            self.hit_event = False
            self.hit_countdown = 0.0
            return (c.END_EVENT, self.data) 
        return (c.CONTINUE_EVENT, '') 