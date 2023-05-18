from entities.mov_object import MovableObject
from components.utils import Utils
from viewport import Viewport
import pygame
import constants as c

class GrowShroom(MovableObject):

    def __init__(self, pos: tuple, event_bus, data="") -> None:
        super().__init__((12, 13), pos, event_bus,id=c.G_SHROOM, data=data, x_offsets=(2, 2), y_offsets=(3, 0))
        self.debug_color = c.SPRING_GREEN
        self.solidAll = False

        self.used = False

        self.visible = False
        self.static = True

        self.spawningCounter = 0.0
        self.startCounter = 0.0

    def texture(self, game_res: dict): return game_res['objects']['shroom']['1']

    def render(self, viewport: Viewport, game_res: dict) -> None:
        if self.visible:
            viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))

    def growshroomEvent(self, dt: float) -> None:
        self.startCounter += dt

        if self.startCounter <= c.MYSBLOCK_ANIMATION_DURATION:
            return (c.CONTINUE_EVENT, '')
        else:
            self.startCounter = c.MYSBLOCK_ANIMATION_DURATION + 1

        self.visible = True
        self.spawningCounter += dt

        movement = Utils.maprange((0.0, c.SHROOM_ANIMATION_DURATION), (0, 13), self.spawningCounter)

        self.changePosition((self.position.x, self.orgPos[1] - movement))

        if self.spawningCounter > c.SHROOM_ANIMATION_DURATION:
            self.spawningCounter = 0.0
            self.static = False
            return (c.END_EVENT, '')
        return (c.CONTINUE_EVENT, '')