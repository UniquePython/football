import random
from enum import auto
from typing import Optional

from enums import BaseEnum


class Role(BaseEnum):
    Attacker = auto()
    Midfielder = auto()
    Defender = auto()
    Keeper = auto()


_ROLE_WEIGHTS = {
    Role.Attacker: 0.30,
    Role.Midfielder: 0.30,
    Role.Defender: 0.30,
    Role.Keeper: 0.10,
}


class Position(BaseEnum):
    ST = auto()
    LW = auto()
    RW = auto()

    LM = auto()
    CM = auto()
    CAM = auto()
    CDM = auto()
    RM = auto()

    LB = auto()
    CB = auto()
    RB = auto()

    GK = auto()

    @property
    def role(self) -> Role:
        return _ROLE_MAP[self]

    @property
    def defensiveness(self) -> float:
        return _DEFENSIVENESS_MAP[self]

    @property
    def offensiveness(self) -> float:
        return (
            2.0 - self.defensiveness if self.role != Role.Keeper else 0.0
        )  # since they sum to 2 always

    @classmethod
    def randomPositionFromRole(cls, role: Optional[Role]) -> "Position":
        if role is None:
            role = random.choices(
                list(_ROLE_WEIGHTS),
                weights=_ROLE_WEIGHTS.values(),
                k=1,
            )[0]

        positions = [p for p in cls if p.role == role]
        return random.choice(positions)

    @classmethod
    def random(cls) -> "Position":
        return cls.randomPositionFromRole(None)


_ROLE_MAP = {
    Position.LW: Role.Attacker,
    Position.ST: Role.Attacker,
    Position.RW: Role.Attacker,
    # ----------------------------
    Position.LM: Role.Midfielder,
    Position.CM: Role.Midfielder,
    Position.CAM: Role.Midfielder,
    Position.CDM: Role.Midfielder,
    Position.RM: Role.Midfielder,
    # ----------------------------
    Position.LB: Role.Defender,
    Position.CB: Role.Defender,
    Position.RB: Role.Defender,
    # ----------------------------
    Position.GK: Role.Keeper,
}

_DEFENSIVENESS_MAP = {
    Position.LB: 2.0,
    Position.CB: 2.0,
    Position.RB: 2.0,
    Position.LM: 1.0,
    Position.CDM: 1.5,
    Position.CM: 1.0,
    Position.CAM: 0.5,
    Position.RM: 1.0,
    Position.LW: 0.0,
    Position.ST: 0.0,
    Position.RW: 0.0,
    Position.GK: 0.0,
}
