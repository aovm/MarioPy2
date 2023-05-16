from entities.kin_object import KinecticObject
from components.utils import Utils
import constants as c
from viewport import Viewport
import pygame

class iBlock(KinecticObject): 

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, c.I_BLOCK, data)
        self.solidAll = False
        self.solidUp = True

        self.orgPos = pygame.Vector2(self.position.x, self.position.y)

        self.invisible = True
        self.used = False
        self.hit_event = False
        self.hit_countdown = 0.0

        self.debug_color = c.BLACK

        self.textureIndex = '4'

    def render(self, viewport: Viewport, game_res: dict) -> None:
        super().render(viewport, game_res)
        if self.used:
            viewport.mapBlit(game_res['blocks']['?block']['4'], (self.position.x, self.position.y))
        else:
            return

    def animationHitEvent(self, dt: float):
        # (0, 6, 0, -1, 0)
        self.hit_countdown += dt
        
        indicator = Utils.maprange((0, c.MYSBLOCK_ANIMATION_DURATION), (0, 16), self.hit_countdown)

        if indicator <= 8:
            self.changePosition((self.position.x, self.orgPos.y - indicator))
        elif indicator <= 14:
            g = Utils.maprange((8, 14), (8, 0), indicator)
            self.changePosition((self.position.x, self.orgPos.y - g ))
        elif indicator <= 15:
            g = Utils.maprange((12, 13), (0, 1), indicator)
            self.changePosition((self.position.x, self.orgPos.y + g ))
        elif indicator <= 16:
            g = Utils.maprange((13, 14), (1, 0), indicator)
            self.changePosition((self.position.x, self.orgPos.y + g ))
        else:
            self.changePosition((self.position.x, self.orgPos.y))
            self.solidAll = True
            self.invisible = False
            self.hit_event = False
            self.hit_countdown = 0.0
            return (c.END_EVENT, self.data) 
        return (c.CONTINUE_EVENT, '') 