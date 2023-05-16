from entities.kin_object import KinecticObject
from components.utils import Utils
import constants as c
from viewport import Viewport
import pygame

class MysteryBlock(KinecticObject):

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, c.Q_BLOCK, data)
        self.used = False
        self.debug_color = c.CYAN

        self.orgPos = pygame.Vector2(self.position.x, self.position.y)

        self.hit_event = False
        self.hit_countdown = 0.0

        self.textureIndex = '1'


    def updateGlobalTextureIndex(self, index_dict: dict):
        if c.Q_BLOCK in index_dict:
            self.textureIndex = index_dict[c.Q_BLOCK][0]
        else:
            print(c.Q_BLOCK, 'no accedió a los indices globales.')
            self.textureIndex = '1'


    def getTexture(self, game_res) -> pygame.Surface:
        if not self.used:
            return game_res['blocks']['?block'][self.textureIndex]
        else:
            return game_res['blocks']['?block']['4']


    def render(self, viewport: Viewport, game_res: dict) -> None:
        super().render(viewport, game_res)
        viewport.mapBlit(self.getTexture(game_res), (self.position.x, self.position.y))


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
            self.used = True
            self.hit_event = False
            self.hit_countdown = 0.0
            return (c.END_EVENT, self.data) 
        return (c.CONTINUE_EVENT, '') 
