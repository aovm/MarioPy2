from entities.mov_object import MovableObject
from entities.kin_object import KinecticObject
from viewport import Viewport
from itertools import cycle
import constants as c
import pygame

class Koopa(MovableObject):

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((14, 10), pos, None, c.KOOPA, data, x_offsets=(1, 1), y_offsets=(6, 0))
        vel_d = -1 if data.lower() == "l" else 1
        self.velocity = pygame.Vector2(vel_d * c.GOOMBA_VEL_X, 0)
        
        self.orgPos = (self.position.x, self.position.y)
        self.orgVelocity = (abs(self.velocity.x), abs(self.velocity.y))

        self.beat = False
        self.solidAll = True

        self.invisibleRect = False

        self.shelled = False
        self.textureShelled = False
        self.shelled_counter = 0.0
        self.almostShelled = False
        self.stompLock = False

        self.streak = 0
        self.shelledMovement = False
        self.shelledMovementLock = False
        self.shelledMovementCounter = 0.0
        
        self.frontFacing = True
        self.flipped = False
        self.solidEntity = True

        self.knocked_counter = 0.0

        self.prev_pos = pygame.Vector2(self.position.x, self.position.y)
        self.walkingCycle = cycle(['1', '2'])
        self.walkingIndex = next(self.walkingCycle)
        self.texture_dist = 0.0
        self.stompFIndex = '4'

    # PROGRAMAR AL FINAL CUANDO SE KNOQUEA POR BLOQUE Y LAS PATAS
    def texture(self, game_res: dict) -> pygame.Surface:
        flipp_x = '_f' if self.frontFacing else ''
        if not self.shelled and not self.textureShelled:
            return pygame.transform.flip(game_res['entities']['koopa'][self.walkingIndex + flipp_x], False, self.flipped)
        elif self.almostShelled:
            return pygame.transform.flip(game_res['entities']['koopa']['4'], False, self.flipped)
        else:
            return pygame.transform.flip(game_res['entities']['koopa']['3'], False, self.flipped)

    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))


    def whenUpCol(self, obj: KinecticObject):
        if (obj.solidAll or obj.solidUp) and obj.block:
            self.velocity.y = 0
            self.position.y = obj.rect.bottom + self.rect.height + self.y_offsets[1]
            self.rect.bottom = self.position.y - self.y_offsets[1]

    def whenDownCol(self, obj: KinecticObject):
        if (obj.solidAll or obj.solidDown) and obj.block:
            self.onGround = True
            self.velocity.y = 0
            self.position.y = obj.rect.top
            self.rect.bottom = self.position.y

    def whenLeftCol(self, obj: KinecticObject):
        if (obj.solidAll or obj.solidLeft) and (obj.block or not self.shelledMovement):
            self.velocity.x = self.orgVelocity[0] if not self.shelled else c.KOOPA_SHELL_VX
            self.position.x = obj.rect.right - self.x_offsets[0] + (1) # EXTRA POS
            self.rect.x = obj.rect.right

    def whenRightCol(self, obj: KinecticObject): 
        if (obj.solidAll or obj.solidRight) and (obj.block or not self.shelledMovement):
            self.velocity.x = -self.orgVelocity[0] if not self.shelled else -c.KOOPA_SHELL_VX
            self.position.x = obj.rect.left - self.rect.w - self.x_offsets[1] + 0.9998 - (1) # EXTRA POS
            self.rect.x = obj.rect.left - self.rect.w


    def update(self, dt: float, objects: list):
        super().update(dt, objects)
        self.texture_dist += abs(self.prev_pos.x - self.position.x)
        self.prev_pos.x = self.position.x
        if self.shelledMovement:
            self.shelled_counter = 0.0
            self.shelledMovementCounter += dt

            if self.shelledMovementCounter > 0.2:
                self.shelledMovementLock = False
        elif not self.static and self.shelled:
            self.shelledMovementCounter = 0.0
            self.shelledMovementLock = False

            self.shelled_counter += dt

            if self.shelled_counter > c.KOOPA_ALMOST_SHELL_TIME:
                self.almostShelled = True

            if self.shelled_counter > c.KOOPA_SHELL_TIME:
                self.shelled_counter = 0.0
                self.shelledMovementCounter = 0.0
                self.unshell()

    def updateTextureIndex(self, dt: float):
        if self.velocity.x == 0:
            self.frontFacing = self.frontFacing
        if self.velocity.x > 0:
            self.frontFacing = True
        else:
            self.frontFacing = False

        if self.shelled:
            self.walkingCycle = cycle(['1', '2'])
        elif self.texture_dist > c.GOOMBA_WALK_TEXT and not self.static:
            self.texture_dist = 0.0
            self.walkingIndex = next(self.walkingCycle)


    def stomp(self, mario_rect: pygame.Rect):
        if not self.shelled:
            self.streak = 0
            self.shelledMovementLock = False
            self.shelledMovement = False
            self.shelled = True
            self.velocity.x = 0
        elif not self.shelledMovement:
            if abs(self.rect.left - mario_rect.left) >= abs(self.rect.left - mario_rect.right):
                self.rightMovement()
            else:
                self.leftMovement()
        else:
            self.streak = 0
            self.shelled = True
            self.shelledMovement = False
            self.shelledMovementLock = False
            self.velocity.x = 0

    
    def rightMovement(self):
        self.shelledMovementLock = True
        self.shelledMovement = True
        self.velocity.x = c.KOOPA_SHELL_VX

    
    def leftMovement(self):
        self.shelledMovementLock = True
        self.shelledMovement = True
        self.velocity.x = -c.KOOPA_SHELL_VX


    def unshell(self):
        self.shelled = False
        self.almostShelled = False
        self.shelledMovement = False
        self.shelledMovementLock = False
        if self.frontFacing:
            self.velocity.x = self.orgVelocity[0]
        else:
            self.velocity.x = -self.orgVelocity[0]
     
    
    def knocked(self, front: bool):
        dir_index = 1 if front else -1

        self.beat = True
        self.static = True
        self.invisibleRect = True
        self.flipped = True
        self.textureShelled = True
        self.shelled = False
        self.orgVelocity = (c.ENTITY_KNOCKED_X * dir_index, -c.ENTITY_KNOCKED_Y)
        self.velocity.x = c.ENTITY_KNOCKED_X * dir_index
        self.velocity.y = -c.ENTITY_KNOCKED_Y

    
    def knockedEvent(self, dt: float):
        self.knocked_counter += dt

        self.invisibleRect = True
        self.textureShelled = True

        self.ver_move(dt)
        self.hor_move(dt)

        if self.knocked_counter > c.KNOCKED_TIME:
            return (c.END_EVENT, '')
        return (c.CONTINUE_EVENT, '')