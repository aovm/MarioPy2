from entities.kin_object import KinecticObject
from components.events import Event
import pygame
import constants as c

class MovableObject(KinecticObject):

    def __init__(self, dimensions: tuple, pos: tuple, event_bus, id="", data="", x_offsets=..., y_offsets=...) -> None:
        super().__init__(dimensions, pos, id, data, x_offsets, y_offsets)
        self.velocity = pygame.Vector2(c.OBJECT_VELOCITY_X, 0)
        self.acceleration = pygame.Vector2(0, c.GRAVITY)

        self.orgPos = (self.position.x, self.position.y)
        self.orgVelocity = (self.velocity.x, self.velocity.y)
        self.orgAcceleration = (self.acceleration.x, self.acceleration.y)
        self.subscribed_event_bus: list = event_bus

        self.notAppeared = True
        self.static = False
        self.onGround = False

        self.block = False

        self.hasFlippedTexture = False
        self.frontFacing = True
        self.debug_color = c.CHARTREUSE

    def changePosition(self, coords):
        super().changePosition(coords)

    def whenUpCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidUp:
            self.velocity.y = 0
            self.position.y = obj.rect.bottom + self.rect.height + self.y_offsets[1]
            self.rect.bottom = self.position.y - self.y_offsets[1]

    def whenDownCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidDown:
            self.onGround = True
            self.velocity.y = 0
            self.position.y = obj.rect.top
            self.rect.bottom = self.position.y

    def whenLeftCol(self, obj: KinecticObject):
        if obj.solidAll or obj.solidLeft:
            self.velocity.x = self.orgVelocity[0]
            self.position.x = obj.rect.right - self.x_offsets[0] + (1) # EXTRA POS
            self.rect.x = obj.rect.right


    def whenRightCol(self, obj: KinecticObject): 
        if obj.solidAll or obj.solidRight:
            self.velocity.x = -self.orgVelocity[0]
            self.position.x = obj.rect.left - self.rect.w - self.x_offsets[1] + 0.9998 - (1) # EXTRA POS
            self.rect.x = obj.rect.left - self.rect.w


    def hor_move(self, dt: float):
        if self.velocity.x >= 0:
            self.frontFacing = True
        else:
            self.frontFacing = False
        self.velocity.x += self.acceleration.x * dt * c.TARGET_FPS
        self.position.x = self.position.x + (self.velocity.x * dt * c.TARGET_FPS) + (self.acceleration.x / 2) * ((dt * c.TARGET_FPS) ** 2)
        self.updateHitboxX()

    def hor_col(self, dt: float, objects: list):
        detected: list[KinecticObject] = self.getCollisions(objects)

        for obj in detected:
            if obj.invisibleRect: continue
            if self.velocity.x >= 0 and abs(obj.rect.left - self.rect.right) < c.COLLISION_TOLERANCE: # Colisión mirando al frente
                # eventRegistry.append((obj, "right", self))
                self.subscribeEvent("collision_right", obj)
                self.whenRightCol(obj)

            elif self.velocity.x <= 0 and abs(obj.rect.right - self.rect.left) < c.COLLISION_TOLERANCE: # Colisión mirando hacia atrás
                # eventRegistry.append((obj, "left", self))
                self.subscribeEvent("collision_left", obj)
                self.whenLeftCol(obj)

    def ver_move(self, dt: float): 
        self.velocity.y += self.acceleration.y * dt * c.TARGET_FPS
        if self.velocity.y > c.MARIO_TOP_FALL_SPEED: self.velocity.y = c.MARIO_TOP_FALL_SPEED
        self.position.y = self.position.y + (self.velocity.y * dt * c.TARGET_FPS) + (self.acceleration.y / 2) * ((dt * c.TARGET_FPS) ** 2)
        self.updateHitboxY()

    def ver_col(self, dt: float, objects: list):
        self.onGround = False
        self.rect.bottom += 1
        detected = self.getCollisions(objects)

        for obj in detected:
            if obj.invisibleRect: continue
            if self.velocity.y > 0 and abs(obj.rect.top - self.rect.bottom) < c.COLLISION_TOLERANCE: # Golpea el piso
                # eventRegistry.append((obj, "down", self)) ; print('down')
                self.subscribeEvent("collision_down", obj)
                self.whenDownCol(obj)
            elif self.velocity.y < 0 and abs(obj.rect.bottom - self.rect.top) < c.COLLISION_TOLERANCE: # Golpe "cabeceo"
                # eventRegistry.append((obj, "up", self)) ; print('up')
                self.subscribeEvent("collision_up", obj)
                self.whenUpCol(obj)


    def updateTextureIndex(self, dt: float): pass
    def update(self, dt: float, objects: list):
        if not self.static:
            self.hor_move(dt)
            self.hor_col(dt, objects)
            self.ver_move(dt)
            self.ver_col(dt, objects)
        self.updateTextureIndex(dt)


    def getCollisions(self, collision_objs: list[KinecticObject]) -> list[KinecticObject]:
        collisions = []
        for obj in collision_objs:
            if self.rect.colliderect(obj.rect): collisions.append(obj)
        return collisions

    
    def subscribeEvent(self, description, other=None):
        if self.subscribed_event_bus != None:
            self.subscribed_event_bus.append(Event(self, description, other))