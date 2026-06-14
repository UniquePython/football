from dataclasses import dataclass, field

from match_event import MatchEvent
from player import Player
from team import Team


@dataclass
class MatchState:
    home: Team
    away: Team

    home_score: int = 0
    away_score: int = 0

    minute: int = 0
    stoppage_time: int = 0

    home_possession_minutes: int = 0

    events: list[MatchEvent] = field(default_factory=list)

    # fatigue --- player -> current fatigue modifier (1.0 = fresh, 0.5 = exhausted)
    home_fatigue: dict[Player, float] = field(default_factory=dict)
    away_fatigue: dict[Player, float] = field(default_factory=dict)

    # cards --- player -> list of cards received
    home_cards: dict[Player, list[str]] = field(default_factory=dict)
    away_cards: dict[Player, list[str]] = field(default_factory=dict)

    # active players --- starts as starters, modified by subs
    home_active: list[Player] = field(default_factory=list)
    away_active: list[Player] = field(default_factory=list)

    home_red_carded: list[Player] = field(default_factory=list)
    away_red_carded: list[Player] = field(default_factory=list)

    # subs remaining
    home_subs_remaining: int = 5
    away_subs_remaining: int = 5

    # stats
    home_shots: int = 0
    away_shots: int = 0
    home_shots_on_target: int = 0
    away_shots_on_target: int = 0
    home_corners: int = 0
    away_corners: int = 0
    home_fouls: int = 0
    away_fouls: int = 0
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    home_offsides: int = 0
    away_offsides: int = 0
    home_throw_ins: int = 0
    away_throw_ins: int = 0

    def __post_init__(self):
        # initialize active players from starters
        self.home_active = list(self.home.starters)
        self.away_active = list(self.away.starters)

        # initialize fatigue at 1.0 for all active players
        for p in self.home_active:
            self.home_fatigue[p] = 1.0
        for p in self.away_active:
            self.away_fatigue[p] = 1.0

    @property
    def score_str(self) -> str:
        return (
            f"{self.home.name} {self.home_score} - {self.away_score} {self.away.name}"
        )

    @property
    def home_possession(self) -> float:
        if self.minute == 0:
            return 0.5
        return self.home_possession_minutes / self.minute

    @property
    def total_minutes(self) -> int:
        return 90 + self.stoppage_time
