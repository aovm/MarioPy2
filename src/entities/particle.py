from viewport import Viewport
import pygame
import constants as c

class ParticleBuilder:
    def __init__(self, id) -> None:
        self.id = id
        self.coords = None
        self.velocity = None
        self.acceleration = None
        self.cycle = None
        self.appear = -1.0
        self.interval = 0.5

    def setPos(self, pos):
        self.coords = pos
        return self

    def setVelocity(self, velocity):
        self.velocity = velocity        
        return self

    def setAcceleration(self, acceleration):
        self.acceleration = acceleration
        return self

    def setTextureCycle(self, cycle):
        self.cycle = cycle
        return self

    def setInterval(self, interval):
        self.interval = interval
        return self

    def setAppearanceTime(self, interval):
        self.appear = interval
        return self

    def end(self):
        return Particle(self.id, self.coords, self.velocity, self.acceleration, self.cycle, self.interval, self.appear)

# SE PUEDA SALIR DEL VIEWPORT (BOOLEANO) Y TENGA UN TIEMPO DE APARICION LA PARTICULA
class Particle:
    def __init__(self, id, init_coords, velocity, acceleration, textureCycle, textureInterval=0.5, appear=-1.0) -> None:
        self.id = id
        self.position = pygame.Vector2(init_coords)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(acceleration)
        self.textureCycle = textureCycle
        self.interval = textureInterval
        self.appear = appear
        self.hasAppearTime = False

        if self.appear != -1.0:
            self.hasAppearTime = True
        self.end = False

        self.appearanceCounter = 0.0
        self.textureCounter = 0.0
        self.textureIndex = '1'


    def update(self, dt: float): # TEXTURE
        self.textureCounter += dt
        
        self.velocity.x += (self.acceleration.x * (dt * c.TARGET_FPS))
        self.velocity.y += (self.acceleration.y * (dt * c.TARGET_FPS))
        self.position.x = self.position.x + self.velocity.x * (dt * c.TARGET_FPS) \
             + (self.acceleration.x / 2) * ((dt * c.TARGET_FPS) ** 2)
        self.position.y = self.position.y + self.velocity.y * (dt * c.TARGET_FPS) \
            + (self.acceleration.y / 2) * ((dt * c.TARGET_FPS) ** 2)

        if self.hasAppearTime:
            self.appearanceCounter += dt
            if self.appearanceCounter > self.appear:
                self.end = True

        if self.textureCounter > self.interval:
            self.textureCounter = 0.0
            self.textureIndex = next(self.textureCycle)

        
    def render(self, viewport: Viewport, game_res: dict):
        if self.id in game_res['objects']:
            texture = game_res['objects'][self.id][self.textureIndex]
            inside_view = viewport.mapBlit(texture, (self.position.x, self.position.y))
            if not inside_view:
                self.end = True
