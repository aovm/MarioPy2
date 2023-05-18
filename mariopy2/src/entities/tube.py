from entities.kin_object import KinecticObject
import constants as c

# WIP, STRUCTURE OBJECT???

# 

# I - IN ==  O - OUT
# H - HORIZONTAL
# V - VERTICAL

# L - LEFT
# R - RIGHT
# U - UP
# D - DOWN

# 1 - TYPE 1 
# 2 - TYPE 2

# CHANNEL _A
# CHANNEL _B

# P - POSITION EXIT
# T _ TUBE EXIT

# EJEMPLO: ENTRADA IHR1_A
# EJEMPLO: SALIDA OHR2_A

class Tube(KinecticObject):

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 16), pos, c.TUBE, data)
        self.debug_color = c.GREEN

    # NO RENDERING REQUIRED
    def render(self, viewport, game_res: dict) -> None: pass