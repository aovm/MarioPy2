from entities.kin_object import KinecticObject
from viewport import Viewport

class OFlag(KinecticObject):
    
    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, "oflag", data=data)
        self.orgPos = (self.position.x, self.position.y)

    def render(self, viewport: Viewport, game_res: dict) -> None:
        viewport.mapBlit(game_res['objects']['oflag'], (self.position.x, self.position.y))