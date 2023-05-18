from entities.mov_object import MovableObject
from entities.kin_object import KinecticObject
from components.utils import Utils
from viewport import Viewport
from itertools import cycle
import pygame
import constants as c

class Star(MovableObject):

    def __init__(self, pos: tuple, event_bus) -> None:
        super().__init__((14, 14), pos, event_bus, c.STAR, x_offsets=(1, 1), y_offsets=(2, 0))
        self.debug_color = c.YELLOW
        self.orgPos = (self.position.x, self.position.y)
        self.velocity = pygame.Vector2(c.STAR_VEL_X, -c.STAR_BUMP_VEL_Y)
        self.orgVelocity = (self.velocity.x, self.velocity.y)
        self.solidAll = False

        self.used = False

        self.visible = False
        self.static = True

        self.spawningCounter = 0.0
        self.startCounter = 0.0

        self.textureCycle = cycle(['1', '2', '3', '4'])
        self.currentTexture = '1'
        self.textureCounter = 0.0
        self.textureInterval = 0.15

    def whenDownCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidDown:
            self.onGround = True
            self.velocity.y = -c.STAR_BUMP_VEL_Y
            self.position.y = obj.rect.top - 2
            self.rect.bottom = self.position.y

    def texture(self, game_res: dict): 
        return game_res['objects']['star'][self.currentTexture]

    def render(self, viewport: Viewport, game_res: dict) -> None:
        if self.visible:
            viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))

    def updateTextureIndex(self, dt: float):
        self.textureCounter += dt

        if self.textureCounter > self.textureInterval:
            self.textureCounter = 0.0
            self.currentTexture = next(self.textureCycle)

    def starEvent(self, dt: float):
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