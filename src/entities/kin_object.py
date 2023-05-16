import pygame
from viewport import Viewport
import constants as c

class KinecticObject:
    
    def __init__(self, dimensions: tuple, pos: tuple, id="", data="", x_offsets=(0, 0), y_offsets=(0, 0)) -> None:
        super().__init__()
        self.id = id
        self.data = data
        self.x_offsets = x_offsets
        self.y_offsets = y_offsets

        self.dimensions = dimensions
        self.position = pygame.Vector2(pos[0], pos[1])
        self.rect: pygame.Rect = pygame.Rect(0, 0, dimensions[0], dimensions[1])
        self.updateHitboxX()
        self.updateHitboxY()
        self.debug_color = c.AZURE

        self.invisibleRect = False

        self.solidAll = True
        self.solidLeft = self.solidRight = self.solidUp = self.solidDown = False
        
        self.verticalBounce = False
        self.horizontalBounce = False

        self.block = True
        self.solidEntity = False

        self.invisible = False

        self.exists = True # SOLO PARA BUSCAR BUGS

    def updateHitboxX(self): self.rect.x = int(self.position.x) + self.x_offsets[0]
    def updateHitboxY(self): self.rect.bottom = int(self.position.y) - self.y_offsets[1]

    def changePosition(self, coords):
        self.position.x = coords[0]
        self.position.y = coords[1]
        self.updateHitboxX()
        self.updateHitboxY()

    def render(self, viewport: Viewport, game_res: dict) -> None: pass

    def renderDebug(self, viewport: Viewport) -> None:
        viewport.blitDebug(self.rect, color=self.debug_color)

    def updateGlobalTextureIndex(self, index_dict: dict): pass

    def __str__(self) -> str:
        return self.id