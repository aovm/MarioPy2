# VIEWPORT NO DEBERÍA MANEJAR TEXTURAS DE ENTIDADES, NI BLOQUES

import pygame
import constants as c

class Viewport:

    def __init__(self, level, tilesize=16, ipos=(0, 0)) -> None:
        self.canvas = pygame.Surface((c.VIEWPORT_WIDTH, c.VIEWPORT_HEIGHT))
        self.canvas = self.canvas.convert_alpha()
        self.level = level

        self.debugFont = pygame.font.SysFont("arial", int(c.sizeUI() * 0.22))

        self.tilesize = tilesize

        self.vpos = pygame.Vector2(ipos[0], ipos[1])

    def getCanvas(self) -> pygame.Surface:
        return self.canvas

    def fill(self, color):
        self.canvas.fill(color)

    def blitDebug(self, rect: pygame.Rect, color=c.AZURE):
        if c.DEBUG_MODE:
            if (self.vpos.x - rect.w) <= rect.x <= (self.vpos.x + c.VIEWPORT_WIDTH + rect.w):
                pygame.draw.rect(self.canvas, color, (rect.x - self.vpos.x, rect.y - self.vpos.y, rect.w, rect.h), width=1)

    def fixedBlit(self, surface: pygame.Surface, fixedPos):
        x = fixedPos[0]
        # y bool BLIT TOO
        if (0 - surface.get_width() < x < c.VIEWPORT_WIDTH + surface.get_width()):
            self.canvas.blit(surface, fixedPos)
            return True
        return False

    def mapBlit(self, surface: pygame.Surface, pos):
        x, y = pos
        if self.isOnViewport(surface, pos):
            self.canvas.blit(surface, (x - self.vpos.x, y - self.vpos.y - surface.get_height()))
            return True
        return False

    def isOnViewport(self, surface: pygame.Surface, pos) -> bool:
        x, y = pos
        onX = (self.vpos.x - surface.get_width() <= x <= self.vpos.x + c.VIEWPORT_WIDTH + surface.get_width())
        onY = (self.vpos.y - surface.get_height() <= y <= self.vpos.y + c.VIEWPORT_HEIGHT + surface.get_height())
        return onX and onY

    def isRectOnViewport(self, rect: pygame.Rect, pos) -> bool:
        x, y = pos
        onX = (self.vpos.x - rect.w <= x <= self.vpos.x + c.VIEWPORT_WIDTH + rect.w)
        onY = (self.vpos.y - rect.h <= y <= self.vpos.y + c.VIEWPORT_HEIGHT + rect.h)
        return onX and onY

    def upscale(self, screen: pygame.Surface) -> pygame.Surface:
        w, h = screen.get_width(), screen.get_height()
        return pygame.transform.scale(self.canvas, (w, h))
