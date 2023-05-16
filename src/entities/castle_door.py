from entities.kin_object import KinecticObject
import constants as c

class CastleDoor(KinecticObject):

    def __init__(self, pos: tuple, data="") -> None:
        super().__init__((16, 32), pos, c.CASTLEDOOR, data, x_offsets=(0, 0), y_offsets=(0, 0))