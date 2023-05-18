import pygame

from entities.mov_object import MovableObject
from components.utils import Utils
from viewport import Viewport
from itertools import cycle
import constants as c

class Flower(MovableObject):

    def __init__(self, pos: tuple, event_bus, data="") -> None:
        super().__init__((14, 14), pos, event_bus, c.FLOWER, data, x_offsets=(1, 1), y_offsets=(2, 0))
        self.orgPos = pygame.Vector2(self.position.x, self.position.y)
        self.velocity = pygame.Vector2(0, 0)
        self.orgVelocity = (0, 0)
        self.solidAll = False

        self.visible = False
        self.static = False

        self.used = False

        self.debug_color = c.VIOLET
        
        self.spawningCounter = 0.0
        self.startCounter = 0.0

        self.textureIndex = '1'
        self.textureCycle = cycle(['1', '2', '3', '4'])
        self.textureCounter = 0.0

    def texture(self, game_res: dict): return game_res['objects']['fireflower'][self.textureIndex]

    def render(self, viewport: Viewport, game_res: dict) -> None:
        if self.visible:
            viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))

    def updateTextureIndex(self, dt: float):
        self.textureCounter += dt

        if self.textureCounter > c.FLOWER_TEXTURE_INTERVAL:
            self.textureCounter = 0.0
            self.textureIndex = next(self.textureCycle)

    def fireflowerEvent(self, dt: float):
        self.startCounter += dt

        if self.startCounter <= c.MYSBLOCK_ANIMATION_DURATION:
            return (c.CONTINUE_EVENT, '')
        else:
            self.startCounter = c.MYSBLOCK_ANIMATION_DURATION + 1

        self.visible = True
        self.spawningCounter += dt

        movement = Utils.maprange((0.0, c.SHROOM_ANIMATION_DURATION), (0, 14), self.spawningCounter)

        self.changePosition((self.position.x, self.orgPos[1] - movement))

        if self.spawningCounter > c.SHROOM_ANIMATION_DURATION:
            self.spawningCounter = 0.0
            self.static = False
            return (c.END_EVENT, '')
        return (c.CONTINUE_EVENT, '')