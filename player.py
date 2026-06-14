import random
from typing import Optional

from age import AgeInput
from attributes import Attributes, AttributeValue
from country import Country
from foot import Foot
from name import Name
from position import Position, Role
from utils import clamp


class Player:
    def __init__(
        self,
        country: Optional[Country],
        age: Optional[AgeInput],
        foot: Optional[Foot],
        position: Optional[Position],
    ) -> None:
        self.country = country or Country.random()
        self.name = Name.generate(self.country)
        self.age = self._generateAge(age)
        self.foot = foot or Foot.random()
        self.position = position or Position.random()
        self.attributes = Attributes.generate(self.position, self.age)

    def _generateAge(self, age: Optional[AgeInput]) -> int:
        if age is None:
            return clamp(16, 40, int(random.normalvariate(24, 4)))

        if isinstance(age, int):
            return clamp(16, 40, age)

        return random.randint(age.min, age.max)

    @property
    def role(self) -> Role:
        return self.position.role

    @property
    def overall(self) -> int:
        return self.attributes.overall(self.position)

    @property
    def potential(self) -> int:
        return self.attributes.potential(self.position)

    @classmethod
    def random(cls) -> "Player":
        return cls(None, None, None, None)

    def __str__(self) -> str:
        return (
            f"{self.name.fullName} | {self.position} | {self.country} | "
            f"Age {self.age} | {self.foot.capitalize()} foot | "
            f"OVR {self.overall} | POT {self.potential}"
        )

    def display(self) -> None:
        a = self.attributes

        def row(label: str, attr: AttributeValue) -> str:
            return f"    {label:<20} {attr.current:>3} / {attr.potential:>3}"

        def header(label: str) -> str:
            return f"\n  {label}"

        lines = [
            f"{self.name.fullName}",
            f"  {self.position.upper()} ({self.position.role.capitalize()}) | "
            f"{self.country.capitalize()} | "
            f"Age {self.age} | "
            f"{self.foot.capitalize()} foot",
            f"  OVR {self.overall}  |  POT {self.potential}",
            header("Pace"),
            row("Sprint Speed", a.pace.sprintSpeed),
            header("Shooting"),
            row("Finishing", a.shooting.finishing),
            row("Shot Power", a.shooting.shotPower),
            row("Long Shots", a.shooting.longShots),
            row("Volleys", a.shooting.volleys),
            header("Passing"),
            row("Vision", a.passing.vision),
            row("Crossing", a.passing.crossing),
            row("Short Passing", a.passing.shortPassing),
            row("Long Passing", a.passing.longPassing),
            header("Dribbling"),
            row("Agility", a.dribbling.agility),
            row("Ball Control", a.dribbling.ballControl),
            row("Dribbling", a.dribbling.dribbling),
            row("Composure", a.dribbling.composure),
            header("Defending"),
            row("Interceptions", a.defending.interceptions),
            row("Standing Tackle", a.defending.standingTackle),
            row("Sliding Tackle", a.defending.slidingTackle),
            row("Heading", a.defending.heading),
            header("Physical"),
            row("Stamina", a.physical.stamina),
            row("Strength", a.physical.strength),
            row("Aggression", a.physical.aggression),
            row("Jumping", a.physical.jumping),
            header("Goalkeeping"),
            row("Diving", a.keeping.diving),
            row("Handling", a.keeping.handling),
            row("Reflexes", a.keeping.reflexes),
            row("Positioning", a.keeping.positioning),
        ]

        print("\n".join(lines))
