import pygame
import constants as c
from itertools import cycle

class Palette:

    def __init__(self) -> None:
        self.target_mario_palette = c.MARIO_PALETTE
        self.flower_mario_palette = c.MARIO_FLOWER_PALETTE

        """self.target_bricks_palette = None ; FUTURE """

        self.star_palette = cycle(c.MARIO_FIRE_STAR_OVERWORLD_PALETTE)
        self.current_star_palette = None

    def toWorldTypePalette(self, mario_surface: pygame.Surface) -> pygame.Surface:
        return mario_surface

    def toFlowerPalette(self, mario_surface: pygame.Surface) -> pygame.Surface:
        return self.replaceSurfaceColors(mario_surface, self.target_mario_palette, self.flower_mario_palette)

    def toNextStarPalette(self, mario_surface: pygame.Surface) -> pygame.Surface:
        self.current_star_palette = next(self.star_palette)
        return self.replaceSurfaceColors(mario_surface, self.target_mario_palette, self.current_star_palette)

    def currentStarPalette(self, mario_surface: pygame.Surface) -> pygame.Surface:
        if self.current_star_palette == None: self.current_star_palette = next(self.star_palette)
        return self.replaceSurfaceColors(mario_surface, self.target_mario_palette, self.current_star_palette)

    def resetStarPalette(self) -> None:
        self.star_palette = cycle(c.MARIO_FIRE_STAR_OVERWORLD_PALETTE)

    """def bricksWorldTypePalette(self, block_surface: pygame.Surface) -> pygame.Surface:
        pass"""

    def replaceSurfaceColors(self, texture: pygame.Surface, colors, rep_colors):
        result = pygame.Surface((texture.get_width(), texture.get_height()))

        pixA = pygame.PixelArray(texture)
        color_layers = []
        index = 0
        for color in colors:
            c_layer_pixA = pixA.extract(color)
            c_layer = c_layer_pixA.make_surface()
            c_layer.set_colorkey((0, 0, 0))

            dPA = pygame.PixelArray(c_layer)
            dPA.replace((255,255,255), rep_colors[index], weights=(0.01, 0.01, 0.01))
            dPA.close()
            color_layers.append(c_layer)
            index += 1
        result.fill(c.ALPHA_COLOR)
        result.set_colorkey(c.ALPHA_COLOR)
        result = result.convert_alpha()
        for layer in color_layers:
            result.blit(layer, (0,0))
        return result

class UndergroundPalette(Palette):

    def __init__(self) -> None:
        super().__init__()
        self.underworld_mario_palette = c.MARIO_UNDERGROUND_PALETTE
        self.star_palette = cycle(c.MARIO_FIRE_STAR_UNDERGROUND_PALETTE)
        self.current_star_palette = None

    def toWorldTypePalette(self, mario_surface: pygame.Surface) -> pygame.Surface:
        return self.replaceSurfaceColors(mario_surface, self.target_mario_palette, self.underworld_mario_palette)

    def resetStarPalette(self) -> None:
        self.star_palette = cycle(c.MARIO_FIRE_STAR_UNDERGROUND_PALETTE)