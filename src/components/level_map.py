from entities.kin_object import KinecticObject
from entities.mov_object import MovableObject
from entities.growshroom import GrowShroom
from entities.lifeshroom import LifeShroom
from entities.flower import Flower
from entities.star import Star
from entities.goomba import Goomba
from entities.koopa import Koopa
from components.palette import Palette, UndergroundPalette
from entities.mysteryblock import MysteryBlock
from entities.particle import Particle, ParticleBuilder
from entities.score import Score, MapScore
from entities.fireball import Fireball
from entities.oflag import OFlag
from entities.castle_door import CastleDoor
import pygame
import constants as c
from itertools import cycle
from viewport import Viewport

class Tile:

    def __init__(self, pos, surface) -> None:
        self.x, self.y = pos
        self.surf: pygame.Surface = surface

    def __str__(self) -> str:
        return f'<{self.x}, {self.y}>'

class LevelMap:

    def __init__(self, tilelist, x_bounds, y_bounds, tilesize, data: dict) -> None:
        self.map_xbounds = x_bounds
        self.map_ybounds = y_bounds

        self.tile_size: int = tilesize

        self.rendered_x1 = -1
        self.rendered_x2 = -1

        # MAP TILES
        self.tiles = tilelist
        self.activeTiles = []

        self.songID = ""
        self.hurrySongID = ""

        # MUSIC DATA??
        if 'map_type' in data:
            if data['map_type'] == c.MAP_OVERWORLD:
                self.palette = Palette()
                self.songID = "1-1_path"
                self.hurrySongID = "1-1_ow_hurry_path"
            elif data['map_type'] == c.MAP_UNDERGROUND:
                self.palette = UndergroundPalette()
                self.songID = "1-1_path_underground"
                self.hurrySongID = "1-1_ug_hurry_path"
        else:
            self.palette = Palette()
            self.songID = "1-1_path"

        # ???
        self.game = None
        self.cLevel = None
        self.castledoor: CastleDoor = None

        self.miniFlag: OFlag = None

        self.globalTextures = {
            c.Q_BLOCK : ['1', 0.0, cycle(['1', '1', '1', '1', '2', '3', '2']), c.GENERAL_TIME_PER_ANIMATION],
            c.COIN : ['1', 0.0, cycle(['1', '1', '1', '1', '2', '3', '2']), c.GENERAL_TIME_PER_ANIMATION]
        }
        self.particleCycle = {
            "bricks_particle" : cycle(['1', '2', '3', '4']),
            "coin_particle" : cycle(['1', '2', '3', '4']),
            "fireball_exp_particle" : cycle(['1', '2', '3'])
        }

        self.running_events = [] # activities???
        
        self.subscribed_event_bus = []

        # CONTAINS IT ALL...
        self.objects: list[KinecticObject] = []
        self.overlay: list[KinecticObject] = []
        # ACTIVE PARTICLES:
        self.activeParticles: list[Particle] = []
        self.activeScores: list[Score] = []
        # ONLY FOR UPDATING MOVEMENT [MovableObject]
        self.entities: list[MovableObject] = [] # REGISTRAR ENTITIES POR SEPARADO
        self.activeEntities: list[MovableObject] = []

    """def reset(self) -> None:
        self.activeTiles = []"""

    def setEntitiesEventBus(self, event_bus):
        for entity in self.entities:
            entity.subscribed_event_bus = event_bus
        self.subscribed_event_bus = event_bus

    def render(self, viewport: Viewport, game_res: dict):
        ### MAP BG RENDERING ###
        self.getActiveTiles(viewport)

        if len(self.activeTiles) != 2: return
        columns, index = self.activeTiles

        canvas = viewport.getCanvas()

        offsetx = viewport.vpos.x
        if viewport.vpos.x < 0:
            offsetx = 0
        elif viewport.vpos.x > len(self.tiles) * self.tile_size - c.VIEWPORT_WIDTH:
            offsetx = len(self.tiles) * self.tile_size - c.VIEWPORT_WIDTH

        x = index * self.tile_size - offsetx
        y = 0 # NO SOPORTA Y CUSTOMS.
        for column in columns:
            for tile_obj in column:
                canvas.blit(tile_obj.surf, (x, y), (0, 0, self.tile_size, self.tile_size))
                y += self.tile_size
            x += self.tile_size
            y = 0

        ### CASTLE DOOR (DEBUG) ###

        if self.castledoor != None:
            viewport.blitDebug(self.castledoor.rect, c.RED)

        ### ENTITIES RENDERING ###

        self.renderEntities(viewport, game_res)

        ### OBJECTS RENDERING ###

        for obj in self.objects:
            obj.updateGlobalTextureIndex(self.globalTextures)
            obj.render(viewport, game_res)
            obj.renderDebug(viewport)


    def renderOverlay(self, viewport: Viewport, game_res: dict):
        for over in self.overlay:
            x, y = (int(over.position.x), int(over.position.y - 16))
            tile = self.tiles[x // 16][y // 16]
            viewport.canvas.blit(tile.surf, (x - viewport.vpos.x, y - viewport.vpos.y), (0, 0, self.tile_size, self.tile_size))

    ### PARTICLE RENDERING (?) ###

    def renderScores(self, viewport: Viewport, game_res: dict):
        for score in self.activeScores:
            score.render(viewport, game_res)

    def renderParticles(self, viewport: Viewport, game_res: dict):
        for particle in self.activeParticles:
            particle.render(viewport, game_res)
    

    def mapWidth(self):
        return len(self.tiles) * self.tile_size


    def updateParticlesScore(self, dt: float, viewport: Viewport):
        for particle in self.activeParticles:
            particle.update(dt)
            if particle.end and particle in self.activeParticles:
                if particle.id == "coin_particle":
                    self.spawnScore("200", (particle.position.x - viewport.vpos.x + 3, particle.position.y - viewport.vpos.y - 6))
                self.activeParticles.remove(particle)
        for score in self.activeScores:
            score.update(dt)
            if score.end and score in self.activeScores:
                self.activeScores.remove(score)


    def isInsideMap(self, rect: pygame.Rect, viewport: Viewport):
        if (self.map_xbounds[0] < rect.right < self.map_xbounds[1]) and (self.map_ybounds[0] < rect.top < self.map_ybounds[1]):
            return True
        return False

    # VIEWPORT (w = 256, h = 240), RENDERED DIMENSIONS (16 + 256 + 16, IGNORE => 16 + 240 + 16)
    def getActiveTiles(self, viewport: Viewport) -> list:
        index: int = (int(viewport.vpos.x) // self.tile_size)
        if index < 0:
            index = 0
        
        self.rendered_x1 = index * self.tile_size

        index2 = index + 19
        if index2 > len(self.tiles):
            index2 = len(self.tiles)
            index = index2 - 19
            
        self.rendered_x2 = (index2 * self.tile_size) - self.tile_size

        columns = []
        #   IT RENDERS 18 TILE COLUMNS (272 px wide)
        for i in range(index, index2):
            columns.append(self.tiles[i])
        
        self.activeTiles = [columns, index]


    def appendMario(self, mario):
        self.objects.append(mario)


    def updateEntities(self, dt: float, viewport: Viewport):
        # DETECT IF ENTITIES ARE IN VIEWPORT...
        for entity in self.entities:
            if viewport.isRectOnViewport(entity.rect, (entity.position.x, entity.position.y))\
                 and entity not in self.activeEntities and entity.notAppeared:
                self.activeEntities.append(entity)
                entity.notAppeared = False
        # ACTIVE ENTITIES.
        for entity in self.activeEntities:
            entries = []
            entries.extend(self.objects)
            entries.extend(self.activeEntities)
            entries.remove(entity)
            entity.update(dt, entries)
            if not viewport.isRectOnViewport(entity.rect, (entity.position.x, entity.position.y)) and entity in self.activeEntities:
                self.activeEntities.remove(entity)
                entity.appeared = False


    def renderEntities(self, viewport: Viewport, game_res: dict):
        for entity in self.activeEntities:
            entity.render(viewport, game_res)
            entity.renderDebug(viewport)


    def removeEntity(self, entity: MovableObject):
        if entity in self.activeEntities:
            self.activeEntities.remove(entity)


    def updateRunningEvents(self, dt: float):
        for run_event in self.running_events:
            event_method = run_event[1]
            status, data = event_method(dt)
            if data == 'entity_remove':
                if run_event[0] in self.activeEntities:
                    self.activeEntities.remove(run_event[0])
            if status == c.END_EVENT and run_event in self.running_events:
                self.running_events.remove(run_event)


    def updateGlobalTextures(self, dt: float):
        for key in self.globalTextures.keys():
            texture_data = self.globalTextures[key]
            # AUMENTAR TIMER
            texture_data[1] += dt

            if texture_data[1] > texture_data[3]:
                texture_data[1] = 0.0
                texture_data[0] = next(texture_data[2])


    def spawnBricksmashParticle(self, pos):
        x, y = pos
        xi, yi = (x + 4, y - 4) 
        
        a = ParticleBuilder("bricks_particle").setPos((xi, yi)).\
            setVelocity((c.BRICKS_PARTICLE_X_VELOCITY, -c.BRICKS_PARTICLE_Y_VELOCITY * 1.3)).setAcceleration((0, c.GRAVITY)).\
            setTextureCycle(self.particleCycle['bricks_particle']).\
            setInterval(c.BRICKS_PARTICLE_TEXTURE_INTERVAL).end()
        b = ParticleBuilder("bricks_particle").setPos((xi, yi)).\
            setVelocity((c.BRICKS_PARTICLE_X_VELOCITY, -c.BRICKS_PARTICLE_Y_VELOCITY)).setAcceleration((0, c.GRAVITY)).\
            setTextureCycle(self.particleCycle['bricks_particle']).\
            setInterval(c.BRICKS_PARTICLE_TEXTURE_INTERVAL).end()
        e = ParticleBuilder("bricks_particle").setPos((xi, yi)).\
            setVelocity((-c.BRICKS_PARTICLE_X_VELOCITY, -c.BRICKS_PARTICLE_Y_VELOCITY * 1.3)).setAcceleration((0, c.GRAVITY)).\
            setTextureCycle(self.particleCycle['bricks_particle']).\
            setInterval(c.BRICKS_PARTICLE_TEXTURE_INTERVAL).end()
        d = ParticleBuilder("bricks_particle").setPos((xi, yi)).\
            setVelocity((-c.BRICKS_PARTICLE_X_VELOCITY, -c.BRICKS_PARTICLE_Y_VELOCITY)).setAcceleration((0, c.GRAVITY)).\
            setTextureCycle(self.particleCycle['bricks_particle']).\
            setInterval(c.BRICKS_PARTICLE_TEXTURE_INTERVAL).end()
    
        self.activeParticles.extend([a, b, e, d])


    def spawnCoinParticle(self, pos):
        x, y = pos
        xi, yi = (x + 4, y - 4)
        coin_p = ParticleBuilder("coin_particle").setPos((xi, yi)).\
                 setVelocity((0, -c.BRICKCOIN_INIT_VELOCITY)).setAcceleration((0, c.BRICK_COIN_GRAVITY)).\
                 setTextureCycle(self.particleCycle['coin_particle']).setInterval(c.BRICKCOIN_TEXTURE_INTERVAL).\
                 setAppearanceTime(c.BRICKCOIN_PARTICLE_DURATION).end()
        self.activeParticles.append(coin_p)


    def spawnFireballParticle(self, rect: pygame.Rect, front: bool):
        fireball_p = Fireball(rect, self.subscribed_event_bus, front=front)
        self.activeEntities.append(fireball_p)


    def spawnFireCollideParticle(self, position: tuple):
        # EMPIEZA JUSTO EN EL X Y Y DE LA REFERENCIA.
        x, y = position
        fireball_p = ParticleBuilder("fireball_exp_particle").setPos((x, y)).\
                setVelocity((0, 0)).setAcceleration((0, 0)).\
                setTextureCycle(self.particleCycle['fireball_exp_particle']).setInterval(c.FIREBALL_TEXT_INT).\
                    setAppearanceTime(c.FIREBALL_COLL_INT).end()
        self.activeParticles.append(fireball_p)
        


    def spawnScore(self, score, i_pos, interval=c.BRICKCOIN_200_PARTICLE_DURATION):
        if score in { "100", "200", "400", "500", "800", "1000", "2000", "4000", "5000", "8000", "1-up" }:
            score = Score(score, i_pos, interval=interval)
            self.activeScores.append(score)


    def spawnMapScore(self, score, i_pos, interval=c.BRICKCOIN_200_PARTICLE_DURATION):
        if score in { "100", "200", "400", "500", "800", "1000", "2000", "4000", "5000", "8000", "1-up" }:
            score = MapScore(score, i_pos, interval=1000)
            self.activeScores.append(score)


    def spawnGrowshroom(self, pos, event_bus):
        shroom = GrowShroom(pos, event_bus)
        self.activeEntities.append(shroom)
        self.running_events.append((shroom, shroom.growshroomEvent))


    def spawnLifeshroom(self, pos, event_bus):
        shroom = LifeShroom(pos, event_bus)
        self.activeEntities.append(shroom)
        self.running_events.append((shroom, shroom.lifeshroomEvent))


    def spawnStar(self, pos, event_bus):
        star = Star(pos, event_bus)
        self.activeEntities.append(star)
        self.running_events.append((star, star.starEvent))

    
    def spawnFireflower(self, pos, event_bus):
        flower = Flower(pos, event_bus)
        self.activeEntities.append(flower)
        self.running_events.append((flower, flower.fireflowerEvent))


    def onStompGoomba(self, goomba: Goomba):
        self.running_events.append((goomba, goomba.stompEvent))

    def onKnockedGoomba(self, goomba: Goomba):
        self.running_events.append((goomba, goomba.knockedEvent))

    def onKnockedKoopa(self, koopa: Koopa):
        self.running_events.append((koopa, koopa.knockedEvent))