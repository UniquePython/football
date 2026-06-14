import random
from enum import auto
from typing import Optional

from faker import Faker

from country import Country
from enums import BaseEnum
from formations import ALL_FORMATIONS, Formation
from name import LOCALE_MAP
from player import Player
from position import Position, Role


class Mentality(BaseEnum):
    VeryAttacking = auto()
    Attacking = auto()
    Balanced = auto()
    Defensive = auto()
    VeryDefensive = auto()

    def __str__(self) -> str:
        _MAP = {
            Mentality.VeryAttacking: "Very Attacking",
            Mentality.Attacking: "Attacking",
            Mentality.Balanced: "Balanced",
            Mentality.Defensive: "Defensive",
            Mentality.VeryDefensive: "Very Defensive",
        }
        return _MAP[self]


MENTALITY_RANGES: dict[Mentality, tuple[float, float]] = {
    Mentality.VeryAttacking: (0.0, 10.9),
    Mentality.Attacking: (11.0, 11.9),
    Mentality.Balanced: (12.0, 12.9),
    Mentality.Defensive: (13.0, 13.9),
    Mentality.VeryDefensive: (14.0, 20.0),
}

TEAM_NAME_SUFFIXES = [
    "FC",
    "United",
    "City",
    "Athletic",
    "Sporting",
    "Rovers",
    "Town",
    "Villa",
]


class Team:
    def __init__(
        self,
        name: Optional[str],
        country: Optional[Country],
        mentality: Optional[Mentality],
    ) -> None:
        self.country = country or Country.random()
        self.name = name or self._generateName(self.country)
        self.mentality = mentality or Mentality.random()
        self.formation = self._selectFormation(self.mentality)
        self.squad = self._generateSquad(self.formation)
        self.starters, self.subs, self.reserves = self._assignSquad()

    def _generateName(self, country: Country) -> str:
        fake = Faker(LOCALE_MAP[country])
        suffix = random.choice(TEAM_NAME_SUFFIXES)
        return f"{fake.city()} {suffix}"

    def _selectFormation(self, mentality: Mentality) -> Formation:
        low, high = MENTALITY_RANGES[mentality]
        candidates = [f for f in ALL_FORMATIONS if low <= f.defensiveness <= high]
        if not candidates:
            candidates = ALL_FORMATIONS
        return random.choice(candidates)

    def _generateSquad(self, formation: Formation) -> list[Player]:
        squad: list[Player] = []
        outfield_positions = formation.positions

        # --- Generate a pool per position: 3 players each ---
        # then assign best as starter, second best as sub
        gk_pool = sorted(
            [Player(self.country, None, None, Position.GK) for _ in range(3)],
            key=lambda p: p.overall,
            reverse=True,
        )
        squad.append(gk_pool[0])  # starter
        sub_gk = gk_pool[1]  # sub

        outfield_subs = []
        for pos in outfield_positions:
            pool = sorted(
                [Player(self.country, None, None, pos) for _ in range(3)],
                key=lambda p: p.overall,
                reverse=True,
            )
            squad.append(pool[0])  # starter
            outfield_subs.append(pool[1])  # sub candidate

        # --- Subs: pick 6 from sub candidates by overall ---
        outfield_subs.sort(key=lambda p: p.overall, reverse=True)
        squad.append(sub_gk)
        squad.extend(outfield_subs[:6])

        # --- Reserves: 12, max 2 GKs ---
        gkCount = 0
        for _ in range(12):
            if gkCount >= 2:
                pos = Position.randomPositionFromRole(
                    random.choice([Role.Attacker, Role.Midfielder, Role.Defender])
                )
            else:
                pos = Position.random()
                if pos == Position.GK:
                    gkCount += 1
            squad.append(Player(self.country, None, None, pos))

        return squad

    def _selectSubPositions(self, outfield_positions: list[Position]) -> list[Position]:
        # Ensure at least 1 defender, 1 midfielder, 1 attacker among subs
        defenders = [p for p in outfield_positions if p.role == Role.Defender]
        midfielders = [p for p in outfield_positions if p.role == Role.Midfielder]
        attackers = [p for p in outfield_positions if p.role == Role.Attacker]

        subs = [
            random.choice(defenders),
            random.choice(midfielders),
            random.choice(attackers),
        ]

        # Fill remaining 3 slots randomly from all outfield positions
        remaining = [p for p in outfield_positions if p not in subs]
        subs += random.sample(remaining, min(3, len(remaining)))

        # If still short, pad with random outfield positions
        while len(subs) < 6:
            subs.append(random.choice(outfield_positions))

        return subs[:6]

    def _assignSquad(self) -> tuple[list[Player], list[Player], list[Player]]:
        starters = self.squad[:11]
        subs = self.squad[11:18]
        reserves = self.squad[18:]
        return starters, subs, reserves

    @property
    def overall(self) -> int:
        return round(sum(p.overall for p in self.starters) / len(self.starters))

    @classmethod
    def random(cls) -> "Team":
        return cls(None, None, None)

    def __str__(self) -> str:
        return (
            f"{self.name} | {self.country.capitalize()} | "
            f"{self.mentality.__str__()} | {self.formation} | "
            f"OVR {self.overall}"
        )

    def display(self) -> None:
        print(f"{self.name}")
        print(
            f"  {self.country.capitalize()} | {self.mentality.__str__()} | {self.formation} | OVR {self.overall}"
        )

        print("\n  Starters")
        for p in self.starters:
            print(
                f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall}  POT {p.potential}"
            )

        print("\n  Subs")
        for p in self.subs:
            print(
                f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall}  POT {p.potential}"
            )

        print("\n  Reserves")
        for p in self.reserves:
            print(
                f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall}  POT {p.potential}"
            )
