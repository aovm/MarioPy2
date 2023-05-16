import gamestates.gamestate as gs
from components.audioplayer import AudioPlayer
from components.level_map import LevelMap
from components.events import Event
from components.utils import Utils
import sys

from entities.kin_object import KinecticObject

from entities.coin import Coin
from entities.mysteryblock import MysteryBlock
from entities.bricks import Bricks
from entities.iblock import iBlock
from entities.growshroom import GrowShroom
from entities.lifeshroom import LifeShroom
from entities.flower import Flower
from entities.star import Star
from entities.goomba import Goomba
from entities.koopa import Koopa
from entities.flag import Flag
from entities.fireball import Fireball
from entities.tube import Tube

from viewport import Viewport
from mario2 import Mario
import random, time
import pygame
import constants as c

# EN UNA TRANSICION DE MAPA O DE STATE, MARIO DEBERÁ
# DEJAR DE MOVERSE.
# TRANSICION / SEQUENCIA (TRANSICION AL NIVEL, MARIO GG, NO SÉ)
class Level1(gs.GameState):

    def __init__(self, game) -> None:
        super().__init__(game)
        self.event_bus: list[Event] = []

        random.seed(time.time())

        self.title = "1-1"
        # 0, 208
        self.mario = Mario(self.game.res, (0, 208), self.event_bus)
        self.audioPlayer = AudioPlayer(self.game.res)
        self.viewport = Viewport(self, ipos=(0, 0))

        self.map_A: LevelMap = self.game.res['1-1']['A']
        self.map_A.appendMario(self.mario)
        self.map_A.setEntitiesEventBus(self.event_bus)
        self.map_B: LevelMap = self.game.res['1-1']['B']
        self.map_B.appendMario(self.mario)
        self.map_B.setEntitiesEventBus(self.event_bus)
        self.currentMap: LevelMap = self.map_A

        self.cIcon = self.game.res['UI']['coin_icon']
        self.xIcon = self.game.res['UI']['x']
        
        self.level_pause = False

        self.flow_phase = 0

        self.first_level_lock = False

        self.transition_counter = 0.0
        self.custom_transition = None
        self.level_transition = True # LEVEL TRANSITIONING. 

        self.level_ticking = True # LEVEL UPDATE BOOL.
        self.level_render = True # LEVEL RENDERING BOOL.

        self.over_data = None


        self.few_time_lock = False
        self.few_time_left = False
        self.few_time_counter = False
        self.last_time_number_str = ''
        self.time_left = 400.0 # 400

        self.updateUIInterval = 0.5
        self.updateUICounter = 0.0
        self.fps = 0.0

        self.escLock = False
        self.empty_keys = pygame.key.get_pressed()

        self.level_flag: Flag = None
        self.first_tube: Tube = None
        self.second_tube: Tube = None
        self.flag_counter = 0.0
        self.flag_text_counter = 0.0
        self.flag_timescore_counter = 0.0
        self.miniflag_counter = 0.0

        self.flag_sprite_counter = 0.0

        self.flag_predown_lock = False
        self.flag_postdown_lock = False

        self.flag_prewalk_lock = False
        self.falg_postwalk_lock = False

        self.flag_vy_lock = False
        self.flag_music_lock = False
        self.flag_music2_lock = False
        self.flag_timescore_done = False

        self.count = 0

        self.after_timescore_counter = 0.0


    def start(self):
        super().start()
        self.playTheme()

        self.level_transition = True
        self.custom_transition = (self.loadingUpdate, self.loadingRender)

    def update(self, dt, keys):
        super().update(dt, keys)
        self.input(keys) # INPUT. NOTA: CONFIGURAR PARA NO MODIFICAR EL MOVIMIENTO
        self.debugUpdate(dt) # ALWAYS UPDATES IN ANY SITUATION.

        if self.level_transition:
            self.custom_transition[0](dt)
            return

        ### LEVEL RUNNING (DOES NOT RUN IN PAUSE)

        if self.level_pause: return

        if self.level_ticking:
            self.updateGametime(dt)
            # PASAR EVENTOS A CURRET MAP UPDATE
            self.updateMario(dt, keys)
            self.currentMap.updateParticlesScore(dt, self.viewport)
            self.currentMap.updateEntities(dt, self.viewport)
            self.currentMap.updateGlobalTextures(dt)
            self.updateEventBus(dt)
            self.currentMap.updateRunningEvents(dt)


    def debugUpdate(self, dt: float):
        self.updateUICounter += dt # TOTAL FPS CALCULATION AND UPDATE
        if self.updateUICounter > self.updateUIInterval:
            self.updateUICounter = 0.0
            self.fps = 1 / (abs(dt) + 0.000000001)


    def render(self, screen: pygame.Surface):
        super().render(screen)

        if self.level_transition:
            self.custom_transition[1](screen)

        if self.level_render:
            self.viewport.fill(c.BLACK)
            self.currentMap.render(self.viewport, self.game.res)
            self.currentMap.renderScores(self.viewport, self.game.res)
            self.mario.renderM(self.viewport)
            self.currentMap.renderOverlay(self.viewport, self.game.res)
            self.currentMap.renderParticles(self.viewport, self.game.res)

            viewportS = self.viewport.upscale(screen)
            screen.blit(viewportS, (0, 0))

            self.renderGUI()


    def input(self, keys):
        if keys[pygame.K_ESCAPE]:
            if not self.escLock:
                self.escLock = True
                self.level_pause = not(self.level_pause)

                self.audioPlayer.playAudio("pause")
                if self.level_pause: self.audioPlayer.pauseMusic()
                else: self.audioPlayer.unpauseMusic()
        else:
            self.escLock = False


    def updateGametime(self, dt: float):
        self.time_left -= dt
        if self.time_left <= 100 and not self.few_time_lock:
            self.few_time_counter += dt
            if not self.few_time_left:
                self.few_time_left = True
                self.audioPlayer.playMusic("warning", 0)

        if self.few_time_counter > 3:
            self.few_time_counter = 0.0
            self.few_time_lock = True
            self.playTheme() # PLAY FAST NORMAL MUSIC

        if self.time_left <= 0:
            self.time_left = 0
            self.level_transition = True
            self.custom_transition = (self.gameoverUpdate, self.gameoverRender)


    def playTheme(self):
        if not self.few_time_lock:
            self.audioPlayer.playMusic(self.currentMap.songID, -1)
        else:
            self.audioPlayer.playMusic(self.currentMap.hurrySongID, -1)


    def updateMario(self, dt: float, keys):
        self.mario.update(dt, keys, self.currentMap, self.viewport, self.audioPlayer)
        if not self.currentMap.isInsideMap(self.mario.rect, self.viewport):
            self.level_transition = True
            self.custom_transition = (self.gameoverUpdate, self.gameoverRender)


    def renderGUI(self):
        self.game.drawUIText("Mario", (60, 23))
        self.game.drawUIText(f"{self.game.totalScore : 07d}", (40, 42))

        self.game.drawUIText("World", (350, 23))
        self.game.drawUIText(self.title, (370, 42))

        self.game.drawUIText("Time", (490, 23)) 
        self.game.drawUIText(f"{int(self.time_left) : 04d}", (490, 42)) 

        self.game.drawUIIcon(self.xIcon, (240, 41))
        self.game.drawUIIcon(self.cIcon, (220, 36))
        self.game.drawUIText(f"{self.game.totalCoins : 03d}", (241, 36))

        if self.level_pause:
            self.game.drawUIText("PAUSE", (260, 300))

        # if c.DEBUG_MODE:
        # self.game.drawUIText("ALPHA", (60, 66))
        self.game.drawUIText(f"FPS: {self.fps : .2f}", (60, 66))
        # self.game.drawUIText(f"X: {self.mario.position.x : .2f}", (60, 126))
        # self.game.drawUIText(f"Y: {self.mario.position.y : .2f}", (60, 156))

    def updateEventBus(self, dt: float):
        for event in self.event_bus:
            ### GRABBED COIN EVENT ###
            if issubclass(type(event.sender), Mario) \
                and issubclass(type(event.other), Coin):

                if event.other in self.currentMap.objects:
                    self.game.totalScore += 200
                    self.addCoinToGame()
                    self.audioPlayer.playAudio("coin")
                    self.currentMap.objects.remove(event.other)

            ### HIT A MYSTERY BLOCK EVENT ###
            if issubclass(type(event.sender), Mario) \
                and issubclass(type(event.other), MysteryBlock) \
                and event.description == "collision_up":

                self.audioPlayer.playAudio("bump")

                if not event.other.used and not event.other.hit_event:
                    event.other.hit_event = True
                    if event.other.data == c.COIN:
                        self.audioPlayer.playAudio("coin")
                        self.addCoinToGame()
                        self.game.totalScore += 200
                        self.currentMap.spawnCoinParticle((event.other.position.x, event.other.position.y))
                    elif event.other.data == c.POWERUP:
                        self.audioPlayer.playAudio("powerup_appear")
                        if self.mario.mario_size == "small":
                            self.currentMap.spawnGrowshroom((event.other.position.x, event.other.position.y - 3), self.event_bus)
                        elif self.mario.mario_size == "big":
                            self.currentMap.spawnFireflower((event.other.position.x, event.other.position.y - 2), self.event_bus)
                    elif event.other.data == c.STAR:
                        self.audioPlayer.playAudio("powerup_appear")
                        self.currentMap.spawnStar((event.other.position.x, event.other.position.y - 2), self.event_bus)
                    self.currentMap.running_events.append((event.other, event.other.animationHitEvent))
            
            ### HIT A BRICK BLOCK EVENT ###
            if issubclass(type(event.sender), Mario) \
                and issubclass(type(event.other), Bricks) \
                and event.description == "collision_up":

                self.audioPlayer.playAudio("bump")

                if event.other.containsItem and not event.other.hit_event and not event.other.used:
                    # EVENT: SPAWN STAR AND APPEAR AS USED.
                    if event.other.data == c.STAR:
                        event.other.hit_event = True
                        self.audioPlayer.playAudio("powerup_appear")
                        event.other.used = True
                        self.currentMap.running_events.append((event.other, event.other.animationHitEvent))
                        self.currentMap.spawnStar((event.other.position.x, event.other.position.y - 2), self.event_bus)
                     # EVENT: HAS COINS, REDUCE COIN COUNT AND APPEAR AS USED.
                    elif event.other.data in { "coin1", "coin5", "coin10", "coin12", "coin20000" }:
                        event.other.hit_event = True
                        self.audioPlayer.playAudio("coin")
                        if event.other.containedCoins > 0:
                            self.game.totalScore += 200
                            self.addCoinToGame()
                            event.other.containedCoins -= 1
                            if event.other.containedCoins == 0:
                                event.other.used = True
                        self.currentMap.running_events.append((event.other, event.other.animationHitEvent))
                        self.currentMap.spawnCoinParticle((event.other.position.x, event.other.position.y))
                else:
                    # EVENT: BREAK AND SPAWN PARTICLES.
                    if self.mario.mario_size == "big" and event.other in self.currentMap.objects and not event.other.used:
                        self.currentMap.objects.remove(event.other)
                        self.audioPlayer.playAudio("bricksmash")
                        self.game.totalScore += 50
                        self.currentMap.spawnBricksmashParticle((event.other.position.x, event.other.position.y))
                    # EVENT: ANIMATE BLOCK MOVEMENT.
                    elif not event.other.hit_event and not event.other.used:
                        event.other.hit_event = True
                        self.currentMap.running_events.append((event.other, event.other.animationHitEvent))
    
            ### HIT AN IBLOCK EVENT ###
            if issubclass(type(event.sender), Mario) \
                and issubclass(type(event.other), iBlock) \
                and event.description == "collision_up":

                self.audioPlayer.playAudio("bump")

                if not event.other.hit_event and not event.other.used:
                    event.other.hit_event = True
                    if event.other.data == c.L_SHROOM:
                        self.audioPlayer.playAudio("powerup_appear")
                        self.currentMap.spawnLifeshroom((event.other.position.x, event.other.position.y - 3), self.event_bus)
                    event.other.invisible = False
                    event.other.used = True
                    self.currentMap.running_events.append((event.other, event.other.animationHitEvent))

            ### MARIO GETS A GROW SHROOM
            if self.reciprocalEventBool(event, Mario, GrowShroom):
                shroom = event.sender if issubclass(type(event.sender), GrowShroom) else event.other
                
                if not shroom.used and shroom in self.currentMap.activeEntities:
                    shroom.used = True
                    self.audioPlayer.playAudio("powerup")
                    self.game.totalScore += 1000
                    self.currentMap.spawnScore("1000", (self.mario.position.x - self.viewport.vpos.x - 1, self.mario.position.y - self.viewport.vpos.y - self.mario.rect.h), c.PARTICLE_1000_DURATION)
                    self.currentMap.activeEntities.remove(shroom)
                    if self.mario.mario_size == "small":
                        self.level_transition = True
                        self.custom_transition = (self.marioBigUpdate, self.marioBigRender)

            ### MARIO GETS WITH LIFESHROOM
            if self.reciprocalEventBool(event, Mario, LifeShroom):
                shroom = event.sender if issubclass(type(event.sender), LifeShroom) else event.other

                if not shroom.used and shroom in self.currentMap.activeEntities:
                    shroom.used = True
                    self.currentMap.spawnScore("1-up", (self.mario.position.x - self.viewport.vpos.x - 1, self.mario.position.y - self.viewport.vpos.y - self.mario.rect.h), c.ONE_UP_PARTICLE_DURATION)
                    self.audioPlayer.playAudio("1-up")
                    self.game.addMarioLive()
                    self.currentMap.activeEntities.remove(shroom)

            ### MARIO GETS FIREFLOWER

            if self.reciprocalEventBool(event, Mario, Flower):
                flower = event.sender if issubclass(type(event.sender), Flower) else event.other

                if not flower.used and flower in self.currentMap.activeEntities:
                    flower.used = True
                    self.audioPlayer.playAudio("powerup")
                    self.game.totalScore += 1000
                    self.currentMap.spawnScore("1000", (self.mario.position.x - self.viewport.vpos.x - 1, self.mario.position.y - self.viewport.vpos.y - self.mario.rect.h), c.PARTICLE_1000_DURATION)
                    self.currentMap.activeEntities.remove(flower)
                    if self.mario.mario_state == 'star':
                        if self.mario.mario_prev_state != 'fire':
                            self.level_transition = True
                            self.custom_transition = (self.marioFlowerUpdate, self.marioFlowerRender)
                    elif self.mario.mario_state != "fire":
                        self.level_transition = True
                        self.custom_transition = (self.marioFlowerUpdate, self.marioFlowerRender)

            ### MARIO GETS STAR

            if self.reciprocalEventBool(event, Mario, Star):
                star = event.sender if issubclass(type(event.sender), Star) else event.other

                if not star.used and star in self.currentMap.activeEntities:
                    star.used = True
                    self.audioPlayer.playMusic("star", -1)
                    self.game.totalScore += 1000
                    self.currentMap.spawnScore("1000", (self.mario.position.x - self.viewport.vpos.x - 1, self.mario.position.y - self.viewport.vpos.y - self.mario.rect.h), c.PARTICLE_1000_DURATION)
                    self.currentMap.activeEntities.remove(star)
                    if self.mario.mario_state != 'star':
                        self.mario.starMario()

            ### MARIO STOPS STAR

            if issubclass(type(event.sender), Mario) and event.description == "star_end":
                self.playTheme()

            ## MARIO GOOMBA
            if self.reciprocalMarioLCollision(event, Goomba) or self.reciprocalMarioRCollision(event, Goomba)\
                 or self.reciprocalMarioUCollision(event, Goomba):
                goomba = event.sender if issubclass(type(event.sender), Goomba) else event.other
                if not goomba.beat:
                    if self.mario.mario_state == "star":
                        self.audioPlayer.playAudio("kick")
                        goomba.knocked(self.mario.facingForward)
                        self.spawnStarStreakScore(goomba.rect)
                        self.currentMap.onKnockedGoomba(goomba)
                    else:
                        self.marioHit()

            if self.reciprocalMarioDCollision(event, Goomba):
                goomba = event.sender if issubclass(type(event.sender), Goomba) else event.other
                if not goomba.beat:
                    if self.mario.mario_state != "star":
                        goomba.stomp()
                        self.audioPlayer.playAudio("stomp")
                        self.mario.bounce()
                        self.spawnMarioStreakScore(goomba)
                        self.currentMap.onStompGoomba(goomba)
                    else:
                        goomba.knocked(self.mario.facingForward)
                        self.audioPlayer.playAudio("kick")
                        self.spawnStarStreakScore(goomba.rect)
                        self.currentMap.onKnockedGoomba(goomba)

            ## MARIO KOOPA
            if self.reciprocalMarioDCollision(event, Koopa):
                koopa = event.sender if issubclass(type(event.sender), Koopa) else event.other

                if self.mario.mario_state != "star":
                    koopa.stomp(self.mario.rect)
                    if not koopa.shelledMovement:
                        self.audioPlayer.playAudio("stomp")
                    else:
                        self.audioPlayer.playAudio("kick")
                    self.mario.bounce()
                    self.spawnKoopaStreakScore(koopa)
                else:
                    self.audioPlayer.playAudio("kick")
                    koopa.knocked(self.mario.facingForward)
                    self.spawnStarStreakScore(koopa.rect)
                    self.currentMap.onKnockedKoopa(koopa)
            elif self.reciprocalMarioLCollision(event, Koopa):
                koopa = event.sender if issubclass(type(event.sender), Koopa) else event.other

                if self.mario.mario_state != "star":
                    if not koopa.shelledMovement and koopa.shelled:
                        koopa.leftMovement()
                        self.audioPlayer.playAudio("kick")
                        self.spawnScore("500", koopa.rect)
                    elif not koopa.static and not koopa.invisibleRect and not koopa.shelledMovementLock:
                        self.marioHit()
                else:
                    self.audioPlayer.playAudio("kick")
                    koopa.knocked(self.mario.facingForward)
                    self.spawnStarStreakScore(koopa.rect)
                    self.currentMap.onKnockedKoopa(koopa)
            elif self.reciprocalMarioRCollision(event, Koopa):
                koopa = event.sender if issubclass(type(event.sender), Koopa) else event.other

                if self.mario.mario_state != "star":
                    if not koopa.shelledMovement and koopa.shelled:
                        koopa.rightMovement()
                        self.audioPlayer.playAudio("kick")
                        self.spawnScore("500", koopa.rect)
                    elif not koopa.static and not koopa.invisibleRect and not koopa.shelledMovementLock:
                        self.marioHit()
                else:
                    self.audioPlayer.playAudio("kick")
                    koopa.knocked(self.mario.facingForward)
                    self.spawnStarStreakScore(koopa.rect)
                    self.currentMap.onKnockedKoopa(koopa)

            if self.reciprocalMarioUCollision(event, Koopa):
                koopa = event.sender if issubclass(type(event.sender), Koopa) else event.other

                if self.mario.mario_state != "star":
                    if not koopa.static or koopa.invisibleRect:
                        self.marioHit()
                else:
                    self.audioPlayer.playAudio("kick")
                    koopa.knocked(self.mario.facingForward)
                    self.spawnStarStreakScore(koopa.rect)
                    self.currentMap.onKnockedKoopa(koopa)


            ## KOOPA VS OTHER ENEMIES. (GOOMBA)
            if self.allCollisions(event, Koopa, Goomba) or self.allCollisions(event, Koopa, Koopa):
                koopa = event.sender if issubclass(type(event.sender), Koopa) else event.other

                if koopa.shelledMovement:
                    if issubclass(type(event.other), Koopa):
                        self.audioPlayer.playAudio("kick")
                        self.spawnKoopaStreakScore(koopa)
                        event.other.knocked(event.sender.frontFacing)
                        self.currentMap.onKnockedKoopa(event.other)
                    elif issubclass(type(event.other), Goomba):
                        self.audioPlayer.playAudio("kick")
                        self.spawnKoopaStreakScore(koopa)
                        event.other.knocked(event.sender.frontFacing)
                        self.currentMap.onKnockedGoomba(event.other)


            ## ENTITIES VS BLOCKS

            if self.blocksHitCollisions(event, Koopa):
                koopa = event.sender

                self.audioPlayer.playAudio("kick")
                self.game.totalScore += 100
                self.spawnScore("100", event.sender.rect)
                event.sender.knocked(event.sender.frontFacing)
                self.currentMap.onKnockedKoopa(event.sender)

            if self.blocksHitCollisions(event, Goomba):
                goomba = event.sender

                self.audioPlayer.playAudio("kick")
                self.game.totalScore += 100
                self.spawnScore("100", event.sender.rect)
                event.sender.knocked(event.sender.frontFacing)
                self.currentMap.onKnockedGoomba(event.sender)

            ## FIREBALL EVENTS

            if self.allCollisions(event, Fireball, Goomba):
                event.sender.invisibleRect = True
                goomba = event.other

                self.audioPlayer.playAudio("kick")
                self.game.totalScore += 100
                self.spawnScore("100", event.other.rect)
                self.currentMap.spawnFireCollideParticle((event.sender.position.x, event.sender.position.y))
                event.other.knocked(event.sender.frontFacing)
                self.currentMap.onKnockedGoomba(event.other)
                self.currentMap.removeEntity(event.sender)

            if self.allCollisions(event, Fireball, Koopa):
                event.sender.invisibleRect = True
                koopa = event.other
                self.game.totalScore += 100
                self.spawnScore("100", event.other.rect)
                self.currentMap.spawnFireCollideParticle((event.sender.position.x, event.sender.position.y))
                self.audioPlayer.playAudio("kick")
                event.other.knocked(event.sender.frontFacing)
                self.currentMap.onKnockedKoopa(event.other)
                self.currentMap.removeEntity(event.sender)

            if issubclass(type(event.sender), Fireball) and \
                issubclass(type(event.other), KinecticObject) and \
                (event.description == "collision_left" or event.description == "collision_right"):

                if event.other.block and not event.sender.used:
                    event.sender.used = True
                    self.currentMap.spawnFireCollideParticle((event.sender.position.x, event.sender.position.y))
                    self.currentMap.removeEntity(event.sender)

            ## TUBE
            if issubclass(type(event.sender), Mario) and\
                issubclass(type(event.other), Tube) and\
                event.description == "collision_down" and self.mario.down:

                self.first_tube = event.other

                if self.currentMap == self.map_A and 916 < self.mario.rect.x and self.mario.rect.right < 940:
                    self.mario.isCrouching = False
                    self.level_transition = True
                    self.audioPlayer.playAudio("pipe")
                    self.custom_transition = (self.tubeToSecondMapUpdate, self.tubeToSecondMapRender)

            if issubclass(type(event.sender), Mario) and\
                issubclass(type(event.other), Tube) and\
                event.description == "collision_right" and self.mario.right:
                
                self.second_tube = event.other

                if self.currentMap == self.map_B and self.mario.onGround:
                    self.audioPlayer.playAudio("pipe")
                    self.level_transition = True
                    self.custom_transition = (self.tubeToFirstMapUpdate, self.tubeToFirstMapRender)


            ## FLAG

            if self.reciprocalMarioRCollision(event, Flag):
                flag = event.sender if issubclass(type(event.sender), Flag) else event.other
                self.mario.isHoldingFlag = True
                self.level_transition = True
                self.level_flag = flag
                self.custom_transition = (self.flagUpdate, self.flagRender)


        self.event_bus.clear()


    def blocksHitCollisions(self, event: Event, sender_type) -> bool:
        sender_t = issubclass(type(event.sender), sender_type)

        block_i = self.blockDownHitCollision(event, iBlock)
        block_b = self.blockDownHitCollision(event, Bricks)
        block_m = self.blockDownHitCollision(event, MysteryBlock)

        return sender_t and (block_i or block_b or block_m)



    def blockDownHitCollision(self, event: Event, other_type) -> bool:
        down = event.description == "collision_down"
        hit = False
        if issubclass(type(event.other), other_type):
            hit = event.other.hit_event
        return down and hit

    def allCollisions(self, event: Event, sender_type, other_type) -> bool:
        a = (issubclass(type(event.sender), sender_type) and issubclass(type(event.other), other_type) and event.description == "collision_left")
        b = (issubclass(type(event.sender), sender_type) and issubclass(type(event.other), other_type) and event.description == "collision_right")
        c = (issubclass(type(event.sender), sender_type) and issubclass(type(event.other), other_type) and event.description == "collision_up")
        d = (issubclass(type(event.sender), sender_type) and issubclass(type(event.other), other_type) and event.description == "collision_down")
        return a or b or c or d


    def reciprocalMarioRCollision(self, event: Event, other_type) -> bool:
        a = (issubclass(type(event.sender), other_type) and issubclass(type(event.other), Mario) and event.description == "collision_left")
        b = (issubclass(type(event.sender), Mario) and issubclass(type(event.other), other_type) and event.description == "collision_right")
        return a or b


    def reciprocalMarioLCollision(self, event: Event, other_type) -> bool:
        a = (issubclass(type(event.sender), other_type) and issubclass(type(event.other), Mario) and event.description == "collision_right")
        b = (issubclass(type(event.sender), Mario) and issubclass(type(event.other), other_type) and event.description == "collision_left")
        return a or b

    
    def reciprocalMarioDCollision(self, event: Event, other_type) -> bool:
        a = (issubclass(type(event.sender), other_type) and issubclass(type(event.other), Mario) and event.description == "collision_up")
        b = (issubclass(type(event.sender), Mario) and issubclass(type(event.other), other_type) and event.description == "collision_down")
        return a or b

    def reciprocalMarioUCollision(self, event: Event, other_type) -> bool:
        a = (issubclass(type(event.sender), other_type) and issubclass(type(event.other), Mario) and event.description == "collision_down")
        b = (issubclass(type(event.sender), Mario) and issubclass(type(event.other), other_type) and event.description == "collision_up")
        return a or b


    def spawnScore(self, quantity: str, reference: pygame.Rect, interval = c.PARTICLE_1000_DURATION):
        ipos = (reference.x - self.viewport.vpos.x, reference.top - self.viewport.vpos.y - 5)
        self.game.totalScore += int(quantity)
        self.currentMap.spawnScore(quantity, ipos, interval=interval)

    
    def spawnScore(self, quantity: str, pos: tuple, interval = c.PARTICLE_1000_DURATION):
        ipos = (pos[0] - self.viewport.vpos.x, pos[1] - self.viewport.vpos.y - 5)
        self.game.totalScore += int(quantity)
        self.currentMap.spawnScore(quantity, ipos, interval=interval)


    def spawnMapScore(self, quantity: str, pos: tuple, interval = c.PARTICLE_1000_DURATION):
        ipos = (pos[0], pos[1])
        self.game.totalScore += int(quantity)
        self.currentMap.spawnMapScore(quantity, ipos, interval = c.PARTICLE_1000_DURATION)


    def spawnStarStreakScore(self, rect: pygame.Rect):
        ipos = (rect.x - self.viewport.vpos.x, rect.top - self.viewport.vpos.y - 5)
        self.mario.starStreak += 1
        if self.mario.starStreak == 1: # 100
            self.game.totalScore += 100
            self.currentMap.spawnScore("100", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 2: # 200
            self.game.totalScore += 200
            self.currentMap.spawnScore("200", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 3: # 400
            self.game.totalScore += 400
            self.currentMap.spawnScore("400", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 4: # 500
            self.game.totalScore += 500
            self.currentMap.spawnScore("500", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 5: # 800
            self.game.totalScore += 800
            self.currentMap.spawnScore("800", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 6: # 1000
            self.game.totalScore += 1000
            self.currentMap.spawnScore("1000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 7: # 2000
            self.game.totalScore += 2000
            self.currentMap.spawnScore("2000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 8: # 4000
            self.game.totalScore += 4000
            self.currentMap.spawnScore("4000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak == 9: # 8000
            self.game.totalScore += 8000
            self.currentMap.spawnScore("8000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.starStreak >= 10: # 1-up
            self.game.addMarioLive()
            self.audioPlayer.playAudio("1-up")
            self.currentMap.spawnScore("1-up", ipos, c.ONE_UP_PARTICLE_DURATION)
        

    def spawnKoopaStreakScore(self, koopa: Koopa):
        ipos = (koopa.rect.x - self.viewport.vpos.x, koopa.rect.top - self.viewport.vpos.y - 5)
        koopa.streak += 1
        if koopa.streak == 1: # 500
            self.game.totalScore += 500
            self.currentMap.spawnScore("500", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak == 2: # 800
            self.game.totalScore += 800
            self.currentMap.spawnScore("800", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak == 3: # 1000
            self.game.totalScore += 1000
            self.currentMap.spawnScore("1000", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak == 4: # 2000
            self.game.totalScore += 2000
            self.currentMap.spawnScore("2000", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak == 5: # 4000
            self.game.totalScore += 4000
            self.currentMap.spawnScore("4000", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak == 6: # 8000
            self.game.totalScore += 8000
            self.currentMap.spawnScore("8000", ipos, c.PARTICLE_1000_DURATION)
        elif koopa.streak >= 7: # 1-up
            self.game.addMarioLive()
            self.audioPlayer.playAudio("1-up")
            self.currentMap.spawnScore("1-up", ipos, c.ONE_UP_PARTICLE_DURATION)


    def spawnMarioStreakScore(self, reference: KinecticObject):
        ipos = (reference.rect.x - self.viewport.vpos.x, reference.rect.top - self.viewport.vpos.y - 5)
        self.mario.marioStreak += 1
        if self.mario.marioStreak == 1: # 100
            self.game.totalScore += 100
            self.currentMap.spawnScore("100", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 2: # 200
            self.game.totalScore += 200
            self.currentMap.spawnScore("200", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 3: # 400
            self.game.totalScore += 400
            self.currentMap.spawnScore("400", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 4: # 500
            self.game.totalScore += 500
            self.currentMap.spawnScore("500", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 5: # 800
            self.game.totalScore += 800
            self.currentMap.spawnScore("800", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 6: # 1000
            self.game.totalScore += 1000
            self.currentMap.spawnScore("1000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 7: # 2000
            self.game.totalScore += 2000
            self.currentMap.spawnScore("2000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 8: # 4000
            self.game.totalScore += 4000
            self.currentMap.spawnScore("4000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.marioStreak == 9: # 8000
            self.game.totalScore += 8000
            self.currentMap.spawnScore("8000", ipos, c.PARTICLE_1000_DURATION)
        elif self.mario.mario_state >= 10: # 1-up
            self.game.addMarioLive()
            self.audioPlayer.playAudio("1-up")
            self.currentMap.spawnScore("1-up", ipos, c.ONE_UP_PARTICLE_DURATION)


    def flagScore(self):
        d = self.mario.rect.top - self.level_flag.rect.top
        x = self.level_flag.rect.right + 4
        ft = self.level_flag.rect.top
        if d <= 0:
            self.game.totalScore += 5000
            self.spawnMapScore("5000", (x, ft))
        elif d <= 16:
            self.game.totalScore += 4000
            self.spawnMapScore("4000", (x, ft + 16))
        elif d <= 32:
            self.game.totalScore += 2000
            self.spawnMapScore("2000", (x, ft + 32))
        elif d <= 48:
            self.game.totalScore += 1000
            self.spawnMapScore("1000", (x, ft + 48))
        elif d <= 64:
            self.game.totalScore += 800
            self.spawnMapScore("800", (x, ft + 64))
        elif d <= 80:
            self.game.totalScore += 500
            self.spawnMapScore("500", (x, ft + 80))
        elif d <= 96:
            self.game.totalScore += 400
            self.spawnMapScore("400", (x, ft + 96))
        elif d <= 112:
            self.game.totalScore += 200
            self.spawnMapScore("200", (x, ft + 112))
        elif d <= 144:
            self.game.totalScore += 100
            self.spawnMapScore("100", (x, ft + 128))


    def marioHit(self):
        if self.mario.mario_state !=  "small":
            self.audioPlayer.playAudio("pipe")
            self.level_transition = True
            self.custom_transition = (self.marioSmallUpdate, self.marioSmallRender)
        else:
            self.level_transition = True
            self.custom_transition = (self.gameoverUpdate, self.gameoverRender)


    def reciprocalEventBool(self, event: Event, sender_type, other_type, looked_desc="") -> bool:
        isCase = False
        if issubclass(type(event.sender), sender_type)\
            and issubclass(type(event.other), other_type):
            isCase = True
        if issubclass(type(event.sender), other_type)\
            and issubclass(type(event.other), sender_type):
            isCase = True
        if looked_desc != "" and isCase:
            if event.description != looked_desc: isCase = False
        return isCase
    

    def addCoinToGame(self):
        self.game.totalCoins += 1
        if self.game.totalCoins >= 100:
            self.game.totalCoins = 0
            self.audioPlayer.playAudio("1-up")
            self.game.addMarioLive()
    

    def loadingRender(self, screen: pygame.Surface): screen.fill(c.SKY)
    def loadingUpdate(self, dt: float):
        self.level_render = False
        self.transition_counter += dt

        if self.transition_counter > c.TRANSITION_INTERVAL:
            self.transition_counter = 0.0
            self.custom_transition = None
            self.level_render = True
            self.level_ticking = True
            self.level_transition = False


    def tubeToSecondMapRender(self, screen: pygame.Surface): pass
    def tubeToSecondMapUpdate(self, dt: float):
        self.transition_counter += dt

        y = Utils.maprange((0, c.SECOND_MAP_TUBE_INT), (self.first_tube.rect.top, self.first_tube.rect.top + 40), self.transition_counter)
        self.mario.position.y = y

        if self.transition_counter > c.SECOND_MAP_INT:
            self.transition_counter = 0.0
            self.mario.position.x = 24
            self.mario.position.y = 32
            self.mario.velocity.y = 0
            self.mario.velocity.x = 0
            self.currentMap = self.map_B
            self.level_transition = False
            self.custom_transition = None
            self.audioPlayer.unloadCurrentMusic()
            self.playTheme()


    def tubeToFirstMapRender(self, screen: pygame.Surface): pass
    def tubeToFirstMapUpdate(self, dt: float):
        self.transition_counter += dt

        if self.transition_counter <= c.FIRST_MAP_FIRST_TUBE_INT:
            x = Utils.maprange((0, c.FIRST_MAP_FIRST_TUBE_INT), (self.second_tube.rect.left - self.mario.rect.width, self.second_tube.rect.left - self.mario.rect.width + 40), self.transition_counter)
            self.mario.position.x = x
        elif self.transition_counter <= c.FIRST_MAP_SECOND_TUBE_INT:
            self.currentMap = self.map_A
            self.viewport.vpos.x = 2494
            yu = Utils.maprange((c.FIRST_MAP_FIRST_TUBE_INT, c.FIRST_MAP_SECOND_TUBE_INT), (176 + 35, 176.2), self.transition_counter)
            y = max(yu, 176.1)
            self.mario.position.x = 2616
            self.mario.position.y = y
            if not self.first_level_lock:
                self.mario.facingForward = True
                self.first_level_lock = True
                self.mario.updateTextures(dt, self.currentMap)
                self.audioPlayer.unloadCurrentMusic()
                self.playTheme()
                self.audioPlayer.playAudio("pipe")

        if self.transition_counter > c.FIRST_MAP_TOTAL_INT:
            self.transition_counter = 0.0
            self.mario.velocity.y = 0
            self.mario.velocity.x = 0
            self.mario.updateHitboxD()
            self.mario.updateHitboxX_M()
            self.mario.updateHitboxY_M()
            self.level_transition = False
            self.custom_transition = None


    def gameoverRender(self, screen: pygame.Surface): pass
    def gameoverUpdate(self, dt: float):
        self.mario.mario_size == "small"
        self.mario.mario_state == "small"

        if self.transition_counter == 0.0:
            self.audioPlayer.unloadCurrentMusic()
            self.audioPlayer.playAudio("mariogg")
            self.mario.gg = True
            self.mario.updateTextures(dt, self.currentMap)
            self.mario.acceleration.y = c.GAME_OVER_GRAVITY
            self.mario.velocity.y = -c.GAME_OVER_Y_VEL

        if self.transition_counter > c.GAME_OVER_FALL_INTERVAL:
            self.mario.vertical_movement(dt)

        self.transition_counter += dt
        if self.transition_counter > c.GAME_OVER_INTERVAL:
            self.transition_counter = 0.0
            self.custom_transition = None
            self.level_render = True
            self.level_ticking = True
            self.level_transition = False
            sys.exit(0)
            # TRANSITION TO LOADING/MENU HERE.


    def flagRender(self, screen: pygame.Surface): pass
    def flagUpdate(self, dt: float):
        self.transition_counter += dt
        self.mario.isCrouching = False
        self.mario.input = False
        self.level_flag.invisibleRect = True
        count = 0

        # DOWN FLAG PHASE (DOWN FLAG AND MARIO GOES DOWN)
        # WALKING PHASE (TO THE CASTLE AND DISAPPEARS, SOUND)
        # TIMESCORE (MARIO ENTERS CASTLE, DISAPPEARS AND TIMESCORE HAPPENS.)

        if not self.flag_music_lock:
            self.flag_music_lock = True
            self.last_time_number_str = str(int(self.time_left) if self.time_left >= 0 else 0)
            if int(self.last_time_number_str[-1]) not in { 1, 3, 6 }:
                self.last_time_number_str = 0
            elif int(self.last_time_number_str[-1]) == 1:
                self.last_time_number_str = 1
            elif int(self.last_time_number_str[-1]) == 3:
                self.last_time_number_str = 3
            elif int(self.last_time_number_str[-1]) == 6:
                self.last_time_number_str = 6
            self.flagScore()
            self.audioPlayer.unloadCurrentMusic()
            self.audioPlayer.playAudio("down_flagpole")
        # DOWN FLAG PHASE
        if self.transition_counter < 1.47:
            self.flag_text_counter += dt

            # POST
            if self.mario.rect.bottom >= self.level_flag.rect.bottom - 4:
                if not self.flag_postdown_lock:
                    self.flag_postdown_lock = True
                    self.mario.facingForward = False
                    self.mario.changePosition((self.mario.position.x + 13, self.level_flag.rect.bottom - 4))
                    self.mario.changeToFlagTexture('8', dt, self.currentMap)
                self.flag_text_counter = 0.0
            else:
                y = self.mario.position.y + c.DOWN_FLAGPOLE_MARIO_VY * (dt * c.TARGET_FPS)
                self.mario.changePosition((self.mario.position.x, y))     

            # FLAG        
            if self.level_flag.flagPos.y < self.level_flag.rect.bottom - 4:
                self.flag_sprite_counter += dt
                offset = Utils.maprange((0, 1.10), (0, 130), self.flag_sprite_counter)
                self.level_flag.flagPos.y = self.level_flag.orgPos.y + offset
            else:
                self.level_flag.flagPos.y = self.level_flag.rect.bottom - 4

            # MARIO MOVEMENT
            if self.flag_text_counter < c.DOWN_FLAGPOLE_TEXT_INTERVAL:
                self.mario.changeToFlagTexture('7', dt, self.currentMap)
            elif self.flag_text_counter <= c.DOWN_FLAGPOLE_TEXT_INTERVAL * 2:
                self.mario.changeToFlagTexture('8', dt, self.currentMap)
            else:
                self.mario.changeToFlagTexture('7', dt, self.currentMap)
                self.flag_text_counter = 0.0
            return
        # WALKING PHASE
        elif self.transition_counter < 1000:
            if not self.flag_prewalk_lock:
                self.flag_prewalk_lock = True
                self.mario.isHoldingFlag = False
                self.mario.isPlayerBraking = True
                self.mario.facingForward = False
                self.mario.velocity.x = 0
                self.mario.changePosition((self.mario.position.x + 12, self.mario.position.y))
            if self.transition_counter < 1.77:
                self.mario.isPlayerBraking = True
                self.mario.update(dt, self.empty_keys, self.currentMap, self.viewport, self.audioPlayer)
            if 1.77 <= self.transition_counter < 3.5:
                if not self.flag_music2_lock:
                    self.flag_music2_lock = True
                    self.audioPlayer.playAudio("stage_clear")
                self.mario.facingForward = True
                self.mario.isPlayerBraking = False
                self.mario.velocity.x = 1.5
                self.mario.update(dt, self.empty_keys, self.currentMap, self.viewport, self.audioPlayer)
            if self.mario.position.x > self.currentMap.castledoor.rect.left:
                self.mario.invisibleMario = True
                if not self.flag_timescore_done:
                    self.miniflag_counter += dt
                    self.flag_timescore_counter += dt
                    
                    yc = Utils.maprange((0, 0.4), (self.currentMap.miniFlag.orgPos[1], self.currentMap.miniFlag.orgPos[1] - 16), self.miniflag_counter)
                    y = max(yc, self.currentMap.miniFlag.orgPos[1] - 16)
                    self.currentMap.miniFlag.changePosition((self.currentMap.miniFlag.position.x, y))

                    if self.flag_timescore_counter > c.FLAGPOLE_TIMESCORE_INT:
                        self.flag_timescore_counter = 0
                        if int(self.time_left) <= 0 and self.miniflag_counter > 0.5:
                            self.time_left = 0
                            self.count = int(self.last_time_number_str)
                            self.flag_timescore_counter = 0.0
                            self.flag_timescore_done = True
                        elif int(self.time_left) > 0:
                            self.game.totalScore += 50
                            self.time_left -= 1
                            self.audioPlayer.playAudio("timescore")
                else:
                    self.currentMap.updateParticlesScore(dt, self.viewport)
                    self.flag_timescore_counter += dt
                    if self.count > 0 and self.flag_timescore_counter > 0.75:
                        self.flag_timescore_counter = 0.0
                        self.game.totalScore += 500
                        self.audioPlayer.playAudio("bump")

                        index = self.count % 6
                        if index == 0:
                            self.currentMap.spawnFireCollideParticle((3248, 60))
                        elif index == 5:
                            self.currentMap.spawnFireCollideParticle((3216, 98))
                        elif index == 4:
                            self.currentMap.spawnFireCollideParticle((3312, 68))
                        elif index == 3:
                            self.currentMap.spawnFireCollideParticle((3318, 114))
                        elif index == 2:
                            self.currentMap.spawnFireCollideParticle((3256, 76))
                        elif index == 1:
                            self.currentMap.spawnFireCollideParticle((3208, 108))
                        self.count -= 1

                    elif self.count <= 0:
                        self.after_timescore_counter += dt

                        if self.after_timescore_counter > c.AFTER_TIMESCORE:
                            self.after_timescore_counter = 0.0
                            sys.exit(0)


    def marioBigRender(self, screen: pygame.Surface): pass
    def marioBigUpdate(self, dt: float):
        self.transition_counter += dt

        currentPhase = int(Utils.maprange((0, c.MARIO_GROWING_TIME), (0, 11), self.transition_counter))

        if currentPhase in [0, 2, 4, 7, 10]:
            self.mario.changeToGrowingTexture(0, dt, self.currentMap)
        elif currentPhase in [1, 3, 5, 8]:
            self.mario.changeToGrowingTexture(1, dt, self.currentMap)
        elif currentPhase in [6, 9, 11]:
            self.mario.changeToGrowingTexture(2, dt, self.currentMap)

        if self.transition_counter > c.MARIO_GROWING_TIME:
            self.mario.bigMario()
            self.transition_counter = 0.0
            self.custom_transition = None
            self.level_ticking = True
            self.level_transition = False


    def marioSmallRender(self, screen: pygame.Surface): pass
    def marioSmallUpdate(self, dt: float):
        self.mario.mario_state = 'big'
        self.transition_counter += dt

        currentPhase = Utils.maprange((0, c.MARIO_DEGROWING_TIME), (0, 11), self.transition_counter)

        invisibilityIndex = random.randint(100, 999)

        if invisibilityIndex % 50 <= 35:
            self.mario.invisibleMario = False
        else:
            self.mario.invisibleMario = True

        # INTERMITENTE???
        if int(currentPhase) in [0, 1, 3, 4, 7, 9]:
            self.mario.changeToDegrowingTexture("big", dt, self.currentMap)
        elif int(currentPhase) in [2, 5, 6, 8, 10, 11, 12, 13]:
            self.mario.changeToDegrowingTexture("small", dt, self.currentMap)

        if self.transition_counter > c.MARIO_DEGROWING_TIME:
            self.mario.resmallMario()
            self.transition_counter = 0.0
            self.custom_transition = None
            self.level_ticking = True
            self.level_transition = False


    def marioFlowerRender(self, screen: pygame.Surface): pass
    def marioFlowerUpdate(self, dt: float):
        self.transition_counter += dt
        
        currentPhase = int(Utils.maprange((0, c.MARIO_GROWING_TIME), (0, 12), self.transition_counter))

        if currentPhase == 0:
            self.flow_phase = currentPhase
            self.mario.image = self.currentMap.palette.currentStarPalette(self.mario.uncolored_image)
        elif currentPhase != self.flow_phase:
            self.flow_phase = currentPhase
            self.mario.image = self.currentMap.palette.toNextStarPalette(self.mario.uncolored_image)

        if self.transition_counter > c.MARIO_GROWING_TIME:
            self.mario.fireMario()
            self.currentMap.palette.resetStarPalette()
            self.transition_counter = 0.0
            self.custom_transition = None
            self.level_ticking = True
            self.level_transition = False


    def tubeVerticalRender(self, screen: pygame.Surface): pass
    def tubeVerticalUpdate(self, dt: float):
        pass


    def tubeHorizontalRender(self, screen): pass
    def tubeHorizontalUpdate(self, dt: float):
        pass