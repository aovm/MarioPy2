from entities.mov_object import MovableObject
from entities.kin_object import KinecticObject
from viewport import Viewport
from itertools import cycle
import constants as c
import pygame

class Fireball(MovableObject):

    def __init__(self, rect: pygame.Rect, event_bus, front=True, data="") -> None:
        super().__init__((8, 8), (rect.x, rect.y), event_bus, c.FIREBALL, data, x_offsets=(0,0), y_offsets=(0,0))
        self.position.x = rect.right if front else rect.left
        self.position.y = rect.top + 4
        self.orgVelocity = (c.FIREBALL_VX, 0)
        self.velocity.x = (c.FIREBALL_VX if front else -c.FIREBALL_VX)
        self.velocity.y = c.OBJECT_BUMP_VELOCITY_Y

        self.frontFacing = True if front else False

        self.stopped = False
        self.solidAll = False
        self.solidEntity = True

        self.texture_cycle = cycle(['1', '2', '3', '4'])
        self.texture_index = next(self.texture_cycle)
        self.texture_counter = 0.0
        self.used = False

    
    def whenUpCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidUp:
            self.velocity.y = 0
            self.position.y = obj.rect.bottom + self.rect.height + self.y_offsets[1]
            self.rect.bottom = self.position.y - self.y_offsets[1]

    def whenDownCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidDown:
            self.onGround = True
            self.velocity.y = -c.FIREBALL_BOUNCE_VY
            self.position.y = obj.rect.top
            self.rect.bottom = self.position.y

    def whenLeftCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidLeft:
            self.velocity.x = 0
            self.position.x = obj.rect.right - self.x_offsets[0] + (1) # EXTRA POS
            self.rect.x = obj.rect.right


    def whenRightCol(self, obj: KinecticObject): 
        if obj.solidAll or obj.solidRight:
            self.velocity.x = 0
            self.position.x = obj.rect.left - self.rect.w - self.x_offsets[1] + 0.9998 - (1) # EXTRA POS
            self.rect.x = obj.rect.left - self.rect.w

    def updateTextureIndex(self, dt: float):
        self.texture_counter += dt
        if self.texture_counter > c.FIREBALL_TEXT_INT:
            self.texture_counter = 0.0
            self.texture_index = next(self.texture_cycle)

    def texture(self, game_res: dict):
        return game_res['objects']['fireball_particle'][self.texture_index]

    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))