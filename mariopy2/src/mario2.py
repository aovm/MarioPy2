import pygame
import constants as c
from entities.kin_object import KinecticObject
from viewport import Viewport
from components.level_map import LevelMap
from components.events import Event
from itertools import cycle
import random, time

class Mario(KinecticObject):

    ## MARIO AS KINECTIC OBJECT???
    def __init__(self, res, ipos, event_bus=None) -> None:
        super().__init__((1, 1), (0, 0), "mario")
        self.mariores: dict = res['mario_states']

        random.seed(time.time())

        self.subscribed_event_bus: list[Event] = event_bus

        self.rectOffsetsX = (2, 2)
        self.rectOffsetsY = (3, 0)

        self.mario_size = "small"
        self.mario_state = "small"
        self.mario_prev_state = None

        self.gg = False

        self.block = False
        self.invisibleRect = False

        self.hasStar = False
        self.starEvent = False
        self.starCounter = 0.0
        self.starStreak = 0

        self.hasCooldown = False
        self.cooldown_counter = 0.0

        self.down = False
        self.right = False

        self.fireballing = False
        self.fireballingLock = False
        self.fireballing_counter = 0.0

        # STREAK DE BUMPS
        self.marioStreak = 0

        # DEPRECATED
        self.signWalkAnim = 1
        self.dist_WalkAnim = 0
        self.walkAnimIndex = 0
        #

        self.starAnimCounter = 0.0

        self.input = True

        self.invisibleMario = False

        self.facingForward = True
        self.onGround = False
        self.isCrouching = False
        self.isJumping = False
        self.isHoldingFlag = False

        self.isPlayerBraking = False

        self.prev_x = 0.0
        self.position = pygame.Vector2(ipos[0], ipos[1])
        self.dt_distance = 0.0
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, c.GRAVITY)
        
        self.uncolored_image: pygame.Surface = self.__getSprite()
        self.image: pygame.Surface = self.__getSprite()
        self.rect = self.image.get_rect()
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def renderM(self, viewport: Viewport):
        if not self.invisibleMario:
            viewport.mapBlit(self.image, (self.position.x, self.position.y))
        viewport.blitDebug(self.rect, c.RED)

    def updateHitboxD(self):
        size = (self.image.get_rect().width - self.rectOffsetsX[0] - self.rectOffsetsX[1], 
                self.image.get_rect().height - self.rectOffsetsY[0] - self.rectOffsetsY[1])
        self.rect.width, self.rect.height = size

    def updateHitboxX_M(self): self.rect.x = int(self.position.x) + self.rectOffsetsX[0]
    def updateHitboxY_M(self): self.rect.bottom = self.position.y

    def update(self, dt: float, keys, level_map: LevelMap, viewport: Viewport, audioplayer):
        if keys[pygame.K_SPACE] and self.input:
            self.jump(audioplayer)
        else:
            if self.isJumping:
                self.velocity.y *= .25
                self.isJumping = False

        if self.onGround: self.marioStreak = 0

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.mario_size == 'big' and self.input: 
            self.isCrouching = True
        else: self.isCrouching = False

        if (keys[pygame.K_DOWN] or keys[pygame.K_s]):
            self.down = True
        else: self.down = False

        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            self.right = True
        else: self.right = False

        if keys[pygame.K_f] and (self.mario_state == 'fire' or self.mario_prev_state == 'fire') and self.input:
            if not self.fireballingLock:
                self.fireball(level_map, audioplayer)
                self.fireballingLock = True
        else: self.fireballingLock = False

        self.updateCooldown(dt)
        self.updateHitboxD()
        self.vertical_movement(dt)
        self.vertical_collision(level_map)
        self.horizontal_movement(dt, keys, viewport, level_map)
        self.horizontal_collision(level_map, viewport)
        self.dt_distance = abs(self.position.x - self.prev_x)
        self.prev_x = self.position.x

        self.updateStatus(dt)
        self.updateTextures(dt, level_map)
    
    def horizontal_movement(self, dt: float, keys, viewport: Viewport, level_map: LevelMap):
        self.acceleration.x = 0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] and self.input:
            self.facingForward = True
            self.isPlayerBraking = True if self.velocity.x < 0 else False

            if self.isCrouching:
                if self.isJumping: self.acceleration.x += c.MARIO_RUN_ACCELERATION
            else:
                self.acceleration.x += c.MARIO_RUN_ACCELERATION
        elif keys[pygame.K_a] or keys[pygame.K_LEFT] and self.input:
            self.facingForward = False
            self.isPlayerBraking = True if self.velocity.x > 0 else False

            if self.isCrouching:
                if self.isJumping: self.acceleration.x -= c.MARIO_RUN_ACCELERATION
            else:
                self.acceleration.x -= c.MARIO_RUN_ACCELERATION
        self.acceleration.x += self.velocity.x * c.MARIO_FRICTION
        if self.isCrouching: self.acceleration.x *= 1.32
        self.velocity.x += self.acceleration.x * (dt * c.TARGET_FPS)
        if self.isCrouching: self.limitVelocity(c.MARIO_TOP_CROUCH_SPEED)
        else: self.limitVelocity(c.MARIO_TOP_RUN_SPEED)

        self.position.x += self.velocity.x * (dt * c.TARGET_FPS) + (self.acceleration.x / 2) * (dt*c.TARGET_FPS) ** 2

        # CAMBIAR COMO METODO DE VIEWPORT
        if self.position.x - viewport.vpos.x > c.VIEWPORT_MARIO_DIST:
            viewport.vpos.x += (self.position.x - viewport.vpos.x - c.VIEWPORT_MARIO_DIST)
        if viewport.vpos.x + c.VIEWPORT_WIDTH > level_map.mapWidth():
            viewport.vpos.x = level_map.mapWidth() - c.VIEWPORT_WIDTH

        # keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.updateHitboxX_M()

    def horizontal_collision(self, level_map: LevelMap, viewport: Viewport):
        if self.position.x < viewport.vpos.x:
            self.position.x = viewport.vpos.x
            self.velocity.x = 0
        allObjs = []
        allObjs.extend(level_map.objects)
        allObjs.extend(level_map.activeEntities)
        detected = self.getCollisions(allObjs)

        for obj in detected:
            if obj.invisibleRect: continue
            if obj.solidEntity and self.hasCooldown: continue
            if obj.solidEntity and self.mario_state == "star": continue
            if self.velocity.x >= 0 and abs(obj.rect.left - self.rect.right) < c.COLLISION_TOLERANCE: # Colisión mirando al frente
                # eventRegistry.append((obj, "right", self))
                self.subscribeEvent("collision_right", obj)

                if obj.solidAll or obj.solidRight:
                    self.velocity.x = 0
                    self.position.x = obj.rect.left - self.rect.w - self.rectOffsetsX[1] + 0.999999
                    self.rect.x = obj.rect.left - self.rect.w

            elif self.velocity.x <= 0 and abs(obj.rect.right - self.rect.left) < c.COLLISION_TOLERANCE: # Colisión mirando hacia atrás
                # eventRegistry.append((obj, "left", self))
                self.subscribeEvent("collision_left", obj)

                if obj.solidAll or obj.solidLeft:
                    self.velocity.x = 0
                    self.position.x = obj.rect.right - self.rectOffsetsX[0]
                    self.rect.x = obj.rect.right
                
    def vertical_movement(self, dt: float):
        self.velocity.y += self.acceleration.y * (dt * c.TARGET_FPS)
        if self.velocity.y > c.MARIO_TOP_FALL_SPEED: self.velocity.y = c.MARIO_TOP_FALL_SPEED
        self.position.y += self.velocity.y * (dt * c.TARGET_FPS) + (self.acceleration.y * .5) * (dt * c.TARGET_FPS) ** 2
        self.updateHitboxY_M()

    def vertical_collision(self, level_map: LevelMap):
        self.onGround = False
        self.rect.bottom += 1

        allObjs = []
        allObjs.extend(level_map.objects)
        allObjs.extend(level_map.activeEntities)
        collidedObjs = self.getCollisions(allObjs)

        for obj in collidedObjs:
            if obj.invisibleRect: continue
            if obj.solidEntity and self.hasCooldown: continue
            if obj.solidEntity and self.mario_state == "star": continue
            if self.velocity.y > 0 and abs(obj.rect.top - self.rect.bottom) < c.COLLISION_TOLERANCE: # Golpea el piso
                # eventRegistry.append((obj, "down", self)) ; print('down')
                self.subscribeEvent("collision_down", obj)

                if obj.solidAll or obj.solidDown:
                    if obj.verticalBounce:
                        self.onGround = False
                        self.velocity.y = -c.MARIO_BOUNCE_Y
                    else:
                        self.onGround = True
                        self.velocity.y = 0
                    self.isJumping = False
                    self.position.y = obj.rect.top
                    self.rect.bottom = self.position.y
            elif self.velocity.y < 0 and abs(obj.rect.bottom - self.rect.top) < c.COLLISION_TOLERANCE: # Golpe "cabeceo"
                # eventRegistry.append((obj, "up", self)) ; print('up')
                self.subscribeEvent("collision_up", obj)

                if obj.solidAll or obj.solidUp:
                    self.isJumping = False
                    self.velocity.y = 0
                    self.position.y = obj.rect.bottom + self.rect.height + self.rectOffsetsY[1]
                    self.rect.bottom = self.position.y - self.rectOffsetsY[1]


    def jump(self, audioplayer):
        if self.onGround:
            self.isJumping = True
            self.velocity.y -= c.BMARIO_JUMP_START if self.mario_size == "big" else c.SMARIO_JUMP_START
            self.onGround = False
            audioplayer.playAudio('jump_big') if self.mario_size == "big" else audioplayer.playAudio('jump_small')


    def bounce(self):
        self.onGround = False
        self.velocity.y = -c.MARIO_BOUNCE_Y


    def fireball(self, level_map: LevelMap, audioplayer):
        self.fireballing = True
        level_map.spawnFireballParticle(self.rect, self.facingForward)
        audioplayer.playAudio("fireball")


    def updateCooldown(self, dt: float):
        if self.hasCooldown:
            self.invisibleRect = True
            self.cooldown_counter += dt

            a = random.randint(100, 999)
            if a % 50 <= 35:
                self.invisibleMario = False
            else:
                self.invisibleMario = True

            if self.cooldown_counter > c.MARIO_INVINCIBILITY_TIME:
                self.cooldown_counter = 0.0
                self.hasCooldown = False
                self.invisibleRect = False
                self.invisibleMario = False

        if self.fireballing:
            self.fireballing_counter += dt
            if self.fireballing_counter > c.MARIO_FIREBALLING_INT:
                self.fireballing_counter = 0.0
                self.fireballing = False


    def getCollisions(self, collision_objs: list) -> list[KinecticObject]:
        collisions = []
        for obj in collision_objs:
            if self.rect.colliderect(obj.rect) and obj.id != "mario": 
                collisions.append(obj)
        return collisions
    
    def limitVelocity(self, maxVelocity):
        self.velocity.x = max(-maxVelocity, min(self.velocity.x, maxVelocity))
        if abs(self.velocity.x) < .08: self.velocity.x = 0

    def updateStatus(self, dt: float):
        if self.hasStar:
            self.starCounter += dt

            if self.starCounter > c.MARIO_STAR_TIME - 0.9:
                if not self.starEvent:
                    self.starEvent = True
                    self.subscribeEvent("star_end", None)

            if self.starCounter > c.MARIO_STAR_TIME:
                self.starCounter = 0.0
                self.destarMario()
                self.starStreak = 0
                self.starEvent = False
                self.hasStar = False

    def subscribeEvent(self, description, other=None):
        if self.subscribed_event_bus != None:
            self.subscribed_event_bus.append(Event(self, description, other))

    def bigMario(self):
        if self.mario_state != 'star':
            self.mario_state = 'big'
            self.mario_size = 'big'
        else:
            self.mario_size = 'big'
            self.mario_prev_state = 'big'
        self.updateHitboxD()
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def resmallMario(self):
        self.invisibleRect = True
        self.hasCooldown = True
        self.mario_prev_state = 'small'
        self.mario_size = 'small'
        self.mario_state = 'small'
        self.updateHitboxD()
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def fireMario(self):
        if self.mario_state != 'star':
            self.mario_size = 'big'
            self.mario_state = 'fire'
        else:
            self.mario_size = 'big'
            self.mario_prev_state = 'fire'
        self.updateHitboxD()
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def defireMario(self):
        self.mario_prev_state = 'big'
        self.mario_size = 'big'
        self.mario_state = 'big'
        self.updateHitboxD()
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def starMario(self):
        self.hasStar = True
        self.mario_prev_state = self.mario_state
        self.mario_state = 'star'

    def destarMario(self):
        self.hasStar = False
        self.starStreak = 0
        self.mario_state = self.mario_prev_state

    ### TEXTURING ###

    def updateTextures(self, dt: float, level_map: LevelMap):
        self.uncolored_image = self.__getSprite()
        self.image = self.__changeColor(dt, level_map)


    def changeToGrowingTexture(self, index: int, dt: float, level_map: LevelMap):
        self.uncolored_image = self.__growingSprite(index)
        self.image = self.__changeColor(dt, level_map)


    def changeToDegrowingTexture(self, size: str, dt: float, level_map: LevelMap):
        self.uncolored_image = self.__degrowingSprite(size)
        self.image = self.__changeColor(dt, level_map)

    
    def changeToFlagTexture(self, variant: str, dt: float, level_map: LevelMap):
        self.uncolored_image = self.__flagSprite(variant)
        self.image = self.__changeColor(dt, level_map)


    def __degrowingSprite(self, size: str) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores[size]['9' + flipTag] 

    
    def __growingSprite(self, index: int): 
        flipTag = '' if self.facingForward else '_f'
        return self.mariores['transition'][str(index) + flipTag]


    def __getSprite(self) -> pygame.Surface:

        def restartTextureVariation():
            self.signWalkAnim = 1
            self.dist_WalkAnim = 0
            self.walkAnimIndex = 0

        if self.gg:
            restartTextureVariation()
            return self.__ggSprite()
        elif self.isHoldingFlag:
            restartTextureVariation()
            return self.__flagSprite('7')
        elif self.fireballing:
            restartTextureVariation()
            return self.__fireballingSprite()
        elif self.isCrouching and self.input:
            restartTextureVariation()
            return self.__crouchingSprite()
        elif self.isJumping or not(self.onGround):
            restartTextureVariation()
            return self.__airSprite()
        elif abs(self.velocity.x) <= 0.4:
            restartTextureVariation()
            return self.__standingSprite()
        elif self.isPlayerBraking:
            restartTextureVariation()
            return self.__brakingSprite()
        else:
            lis = self.__generateWalkSequence()
            
            # print(f'<distWalkAnim: {self.dist_WalkAnim}, index: {self.walkAnimIndex}, sign: {self.signWalkAnim}>')

            if self.dist_WalkAnim == 0:
                self.walkAnimIndex += 1 * self.signWalkAnim
                if self.walkAnimIndex + 1 > len(lis):
                    self.walkAnimIndex = len(lis) - 1
                    self.signWalkAnim = -1
                elif self.walkAnimIndex - 1 < 0:
                    self.walkAnimIndex = 0
                    self.signWalkAnim = 1

            self.dist_WalkAnim += self.dt_distance
            currentTexture = lis[self.walkAnimIndex]
            if c.MARIO_DIST_PER_WALK_ANIMATION < self.dist_WalkAnim:
                self.dist_WalkAnim = 0
            return currentTexture
    
    def __generateWalkSequence(self) -> list:
        flipTag = '' if self.facingForward else '_f'

        return [   self.mariores[self.mario_size]['1' + flipTag],
                self.mariores[self.mario_size]['2' + flipTag],
                self.mariores[self.mario_size]['3' + flipTag],
                self.mariores[self.mario_size]['2' + flipTag] ]
        
    def __standingSprite(self) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores[self.mario_size]['0' + flipTag]

    def __airSprite(self) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores[self.mario_size]['5' + flipTag]

    def __brakingSprite(self) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores[self.mario_size]['4' + flipTag]

    def __flagSprite(self, variant: str) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores[self.mario_size][variant + flipTag]

    def __crouchingSprite(self) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores['big']['6' + flipTag]

    def __fireballingSprite(self) -> pygame.Surface:
        flipTag = '' if self.facingForward else '_f'
        return self.mariores['big']['fireball' + flipTag]

    def __ggSprite(self) -> pygame.Surface:
        return self.mariores['small']['6']

    def __changeColor(self, dt: float, level_map: LevelMap):
        def restartStarCounter():
            self.starAnimCounter = 0.0
            level_map.palette.resetStarPalette()

        if self.mario_state == "fire":
            restartStarCounter()
            return level_map.palette.toFlowerPalette(self.uncolored_image)
        elif self.mario_state == "star":
            self.starAnimCounter += dt
            if self.starAnimCounter > c.MARIO_BETWEEN_STAR_ANIMATION:
                self.starAnimCounter = 0.0
                return level_map.palette.toNextStarPalette(self.uncolored_image)
            return level_map.palette.currentStarPalette(self.uncolored_image)
        else:
            restartStarCounter()
            return level_map.palette.toWorldTypePalette(self.uncolored_image)

    def changePosition(self, coords):
        self.position.x = coords[0]
        self.position.y = coords[1]
        self.updateHitboxX_M()
        self.updateHitboxY_M()

    def updateGlobalTextureIndex(self, index_dict: dict): pass
    def updateHitboxX(self): pass
    def updateHitboxY(self): pass
    def render(self, a, b) -> None: pass

    def __str__(self) -> str:
        return f"Mario<{self.position.x}, {self.position.y}>"