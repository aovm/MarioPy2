from entities.kin_object import KinecticObject
from viewport import Viewport

import constants as c
import pygame

class Coin(KinecticObject):
    
    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, c.COIN, data)
        self.grabbed = False
        self.solidAll = False

        self.debug_color = c.ROSE

        self.textureIndex = '1'

    def updateGlobalTextureIndex(self, index_dict: dict):
        if c.COIN in index_dict:
            self.textureIndex = index_dict[c.COIN][0]
        else:
            print(c.COIN, 'no pudo acceder al indice global.')
            self.textureIndex = '1'

    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(game_res['blocks']['coin'][self.textureIndex], (self.position.x, self.position.y))
