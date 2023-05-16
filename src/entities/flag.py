from entities.kin_object import KinecticObject
from viewport import Viewport
import constants as c
import pygame

class Flag(KinecticObject):

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((4, 144), pos, c.FLAG, data, x_offsets=(2, 0))
        self.orgPos = pygame.Vector2(self.position.x - 12, self.position.y - self.rect.height + 17)
        self.flagPos = pygame.Vector2(self.position.x - 12, self.position.y - self.rect.height + 17)

    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(game_res['objects']['flag'], (self.flagPos.x, self.flagPos.y))
