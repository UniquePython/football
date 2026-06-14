import random
from enum import StrEnum, auto


class Foot(StrEnum):
    Left = auto()
    Right = auto()
    Both = auto()

    @classmethod
    def random(cls):
        return random.choices(
            [cls.Left, cls.Right, cls.Both], weights=[18, 80, 2], k=1
        )[0]
