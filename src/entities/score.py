from viewport import Viewport
from components.utils import Utils
import constants as c
import pygame

class Score:

    def __init__(self, data, init_coords, targetCoords=(0, 0),\
                 interval = (c.BRICKCOIN_200_PARTICLE_DURATION)) -> None:
        self.fixed_pos = pygame.Vector2(init_coords)
        x, y = init_coords
        self.orgPos = (x, y - 10)
        if targetCoords == (0, 0):
            self.target_pos = pygame.Vector2(self.fixed_pos.x, self.fixed_pos.y - 48)
        else:
            self.target_pos = pygame.Vector2(targetCoords)
        self.data = data

        self.end = False

        self.interval = interval
        self.counter = 0.0

    def render(self, viewport: Viewport, game_res: dict):
        viewport.fixedBlit(game_res['objects']['scores'][self.data], (self.fixed_pos.x, self.fixed_pos.y))

    def update(self, dt: float):
        self.counter += dt

        x = Utils.maprange((0.0, c.BRICKCOIN_PARTICLE_DURATION), (self.orgPos[0], self.target_pos.x), self.counter)
        y = Utils.maprange((0.0, c.BRICKCOIN_PARTICLE_DURATION), (self.orgPos[1], self.target_pos.y), self.counter)

        self.fixed_pos.x = x
        self.fixed_pos.y = y

        if self.counter > self.interval:
            self.end = True

class MapScore(Score):

    def __init__(self, data, init_coords, targetCoords=(0, 0), interval=c.BRICKCOIN_200_PARTICLE_DURATION) -> None:
        super().__init__(data, init_coords, targetCoords, interval)
        self.map_pos = pygame.Vector2(init_coords[0], init_coords[1])
        self.target_pos.x = targetCoords[0]
        self.target_pos.y = targetCoords[1]

        self.currentPos = pygame.Vector2(init_coords[0], init_coords[1])

        self.end = False

    def render(self, viewport: Viewport, game_res: dict):
        viewport.mapBlit(game_res['objects']['scores'][self.data], (self.currentPos.x, self.currentPos.y))

    def update(self, dt: float):
        self.counter += dt
        if self.counter > self.interval:
            self.end = True