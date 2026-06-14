import random
from enum import Enum, auto


class Foot(Enum):
    Left = auto()
    Right = auto()
    Both = auto()

    @classmethod
    def random(cls):
        return random.choices(
            [cls.Left, cls.Right, cls.Both], weights=[18, 80, 2], k=1
        )[0]
