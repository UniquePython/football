import random
from enum import StrEnum


class BaseEnum(StrEnum):
    @classmethod
    def random(cls):
        return random.choice(list(cls))
