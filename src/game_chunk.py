import pygame
# Chunks en general de 64 px de largo y 240 px de altura.

class Chunk:

    def __init__(self, index : int, start_coord_x : int, containing_bg : pygame.Surface, width: int, height : int) -> None:
        self.map_index = index
        self.chunk_X = start_coord_x
        self.containing_bg_surface = containing_bg
        self.width = width
        self.height = height
        
        # WORLD -> OBJECTS
        # BLOCKS: (type_block, x, y, isEnabled, )
        self.chunkObjects = []
        self.flag = None
    
    def getSurface(self):
        return self.containing_bg_surface

    def __str__(self) -> str:
        return f"Chunk<Index:{self.map_index}, chunk_X:{self.chunk_X}, width:{self.width}, height:{self.height}, ground:{len(self.ground_hitboxes)}>"