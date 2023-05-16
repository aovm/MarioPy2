from entities.mov_object import MovableObject
from viewport import Viewport
from itertools import cycle
import constants as c
import pygame

class Goomba(MovableObject): 
    
    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((14, 10), pos, None, c.GOOMBA, data=data, x_offsets=(1, 1), y_offsets=(6, 0))
        vel_d = -1 if data.lower() == "l" else 1
        self.velocity = pygame.Vector2(vel_d * c.GOOMBA_VEL_X, 0)

        self.orgPos = (self.position.x, self.position.y)
        self.orgVelocity = (abs(self.velocity.x), abs(self.velocity.y))

        self.down = False
        self.flipped = False

        self.beat = False
        self.solidAll = True

        self.solidEntity = True

        self.orgPos = pygame.Vector2(self.position.x, self.position.y)
        self.textureCycle = cycle(['1', '2'])
        self.textureIndex = next(self.textureCycle)
        self.texture_dist = 0.0

        self.knocked_counter = 0.0
        self.stomp_counter = 0.0

    def texture(self, game_res: dict):
        if not self.down:
            return pygame.transform.flip(game_res['entities']['goomba'][self.textureIndex], False, self.flipped)
        return game_res['entities']['goomba']['3']


    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(self.texture(game_res), (self.position.x, self.position.y))

    
    def knocked(self, front: bool):
        dir_index = 1 if front else -1

        self.beat = True
        self.static = True
        self.invisibleRect = True
        self.flipped = True
        self.orgVelocity = (c.ENTITY_KNOCKED_X * dir_index, -c.ENTITY_KNOCKED_Y)
        self.velocity.x = c.ENTITY_KNOCKED_X * dir_index
        self.velocity.y = -c.ENTITY_KNOCKED_Y


    def knockedEvent(self, dt: float):
        self.knocked_counter += dt

        self.ver_move(dt)
        self.hor_move(dt)

        if self.knocked_counter > c.KNOCKED_TIME:
            return (c.END_EVENT, '')
        return (c.CONTINUE_EVENT, '')
    

    def stomp(self):
        self.beat = True
        self.down = True
        self.invisibleRect = True
        self.static = True
        self.solidAll = False
        self.orgVelocity = (0, 0)
        self.velocity.x = 0
        self.rect.height = 6
        self.updateHitboxX()
        self.updateHitboxY()


    def stompEvent(self, dt: float):
        self.stomp_counter += dt
        if self.stomp_counter > c.GOOMBA_STOMPTIME:
            self.stomp_counter = 0.0
            return (c.END_EVENT, 'entity_remove')
        return (c.CONTINUE_EVENT, '')


    def update(self, dt: float, objects: list):
        super().update(dt, objects)
        self.texture_dist += abs(self.orgPos.x - self.position.x)
        self.orgPos.x = self.position.x


    def updateTextureIndex(self, dt: float):
        if self.texture_dist > c.GOOMBA_WALK_TEXT and not self.static:
            self.texture_dist = 0.0
            self.textureIndex = next(self.textureCycle)