from dataclasses import dataclass
from enum import auto
from typing import Optional

from enums import BaseEnum
from player import Player
from team import Team


class EventType(BaseEnum):
    Goal = auto()
    ShotOnTarget = auto()
    ShotOffTarget = auto()
    Corner = auto()
    ThrowIn = auto()
    Foul = auto()
    YellowCard = auto()
    RedCard = auto()
    Offside = auto()
    Substitution = auto()
    Save = auto()


@dataclass
class MatchEvent:
    minute: int
    type: EventType
    team: Team
    primary_player: Player
    secondary_player: Optional[Player] = None
    description: str = ""
