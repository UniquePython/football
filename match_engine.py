import math
import random
from typing import Optional

from match_event import EventType, MatchEvent
from match_state import MatchState
from player import Player
from position import Position, Role
from team import Team

# ─── Helpers ────────────────────────────────────────────────


def _fatigue(stamina: int, minute: int) -> float:
    decay_rate = 1.0 - (stamina / 100) * 0.5
    return max(0.5, 1.0 - decay_rate * (minute / 90))


def _attr(player: Player, attribute: float, fatigue: float) -> float:
    """Apply fatigue modifier to an attribute value."""
    return attribute * fatigue


def _normalize(*values: float) -> float:
    """Normalize a set of values to a 0-1 probability."""
    return sum(values) / (len(values) * 100)


def _players_by_role(players: list[Player], role: Role) -> list[Player]:
    return [p for p in players if p.role == role]


def _best_player(
    players: list[Player], fatigue: dict[Player, float]
) -> Optional[Player]:
    if not players:
        return None
    return max(players, key=lambda p: p.overall * fatigue.get(p, 1.0))


def _weighted_choice(probability: float) -> bool:
    """Returns True with the given probability (0.0 to 1.0)."""
    return random.random() < probability


# ─── Possession ─────────────────────────────────────────────


def _possession_probability(state: MatchState) -> float:
    """Returns probability that home team has possession this minute."""

    def midfield_strength(players: list[Player], fatigue: dict[Player, float]) -> float:
        mids = _players_by_role(players, Role.Midfielder)
        if not mids:
            return 50.0
        return sum(
            (
                _attr(p, p.attributes.passing.vision.current, fatigue.get(p, 1.0))
                + _attr(
                    p, p.attributes.passing.shortPassing.current, fatigue.get(p, 1.0)
                )
                + _attr(p, p.attributes.physical.stamina.current, fatigue.get(p, 1.0))
            )
            / 3
            for p in mids
        ) / len(mids)

    home_mid = midfield_strength(state.home_active, state.home_fatigue)
    away_mid = midfield_strength(state.away_active, state.away_fatigue)

    # formation modifier
    home_form = state.home.formation.offensiveness * 0.5
    away_form = state.away.formation.offensiveness * 0.5

    # game state modifier — losing team pushes forward
    if state.home_score < state.away_score:
        home_boost = 0.05
    elif state.home_score > state.away_score:
        home_boost = -0.05
    else:
        home_boost = 0.0

    home_strength = home_mid + home_form
    away_strength = away_mid + away_form

    base = home_strength / (home_strength + away_strength)
    return max(0.35, min(0.65, base + home_boost))


# ─── Stoppage Time ──────────────────────────────────────────


def _calculate_stoppage(state: MatchState) -> int:
    base = random.randint(1, 5)
    events = len(
        [
            e
            for e in state.events
            if e.type in (EventType.Goal, EventType.RedCard, EventType.Substitution)
        ]
    )
    return base + events // 3


# ─── Substitution ───────────────────────────────────────────


def _check_substitutions(
    state: MatchState, team: Team, is_home: bool
) -> Optional[MatchEvent]:
    subs_remaining = state.home_subs_remaining if is_home else state.away_subs_remaining
    if subs_remaining <= 0:
        return None

    active = state.home_active if is_home else state.away_active
    fatigue = state.home_fatigue if is_home else state.away_fatigue
    cards = state.home_cards if is_home else state.away_cards
    available_subs = team.subs

    # players who came on as subs — never sub them off
    already_subbed_on = {
        e.secondary_player
        for e in state.events
        if e.type == EventType.Substitution
        and e.team == team
        and e.secondary_player is not None
    }

    outfield = [
        p for p in active if p.position != Position.GK and p not in already_subbed_on
    ]

    # fatigue threshold
    tired = [p for p in outfield if fatigue.get(p, 1.0) < 0.75 and state.minute >= 40]

    # on yellow and game is tight — risk management
    on_yellow_risk = [
        p for p in outfield if "yellow" in cards.get(p, []) and state.minute >= 60
    ]

    # scoreline trigger
    scoreline_trigger = state.minute >= 60 and (
        (is_home and state.home_score < state.away_score)
        or (not is_home and state.away_score < state.home_score)
    )

    # priority: tired > yellow risk > scoreline
    if tired:
        sub_off = min(tired, key=lambda p: fatigue.get(p, 1.0))
    elif on_yellow_risk:
        sub_off = on_yellow_risk[0]
    elif scoreline_trigger:
        sub_off = min(outfield, key=lambda p: p.overall)
    else:
        return None

    # find best available sub for that position
    already_used = [
        e.secondary_player
        for e in state.events
        if e.type == EventType.Substitution and e.team == team
    ]

    available = [
        p
        for p in available_subs
        if p.position == sub_off.position and p not in active and p not in already_used
    ]

    if not available:
        return None

    sub_on = max(available, key=lambda p: p.overall)

    active.remove(sub_off)
    active.append(sub_on)
    fatigue[sub_on] = 1.0
    fatigue.pop(sub_off, None)

    if is_home:
        state.home_subs_remaining -= 1
    else:
        state.away_subs_remaining -= 1

    return MatchEvent(
        minute=state.minute,
        type=EventType.Substitution,
        team=team,
        primary_player=sub_off,
        secondary_player=sub_on,
        description=f"{state.minute}' SUB - {sub_off.name.fullName} → {sub_on.name.fullName} ({team.name})",
    )


# ─── Attack Chain ────────────────────────────────────────────


def _pick_attacker(
    players: list[Player], fatigue: dict[Player, float]
) -> Optional[Player]:
    attackers = _players_by_role(players, Role.Attacker)
    if not attackers:
        return None
    # weighted by finishing + dribbling + composure, modified by fatigue
    weights = [
        math.sqrt(
            (
                _attr(p, p.attributes.shooting.finishing.current, fatigue.get(p, 1.0))
                + _attr(
                    p, p.attributes.dribbling.dribbling.current, fatigue.get(p, 1.0)
                )
                + _attr(
                    p, p.attributes.dribbling.composure.current, fatigue.get(p, 1.0)
                )
            )
        )
        * random.uniform(0.7, 1.3)
        for p in attackers
    ]
    return random.choices(attackers, weights=weights)[0]


def _pick_midfielder(
    players: list[Player], fatigue: dict[Player, float]
) -> Optional[Player]:
    mids = _players_by_role(players, Role.Midfielder)
    if not mids:
        return None
    weights = [
        math.sqrt(
            (
                _attr(p, p.attributes.passing.vision.current, fatigue.get(p, 1.0))
                + _attr(
                    p, p.attributes.passing.shortPassing.current, fatigue.get(p, 1.0)
                )
            )
        )
        * random.uniform(0.7, 1.3)
        for p in mids
    ]
    return random.choices(mids, weights=weights)[0]


def _pick_defender(
    players: list[Player], fatigue: dict[Player, float]
) -> Optional[Player]:
    defenders = _players_by_role(players, Role.Defender)
    if not defenders:
        return None
    weights = [
        math.sqrt(
            (
                _attr(
                    p, p.attributes.defending.interceptions.current, fatigue.get(p, 1.0)
                )
                + _attr(
                    p,
                    p.attributes.defending.standingTackle.current,
                    fatigue.get(p, 1.0),
                )
            )
        )
        * random.uniform(0.7, 1.3)
        for p in defenders
    ]
    return random.choices(defenders, weights=weights)[0]


def _pick_wide_player(
    players: list[Player], fatigue: dict[Player, float]
) -> Optional[Player]:
    """Pick a wide player for crossing situations — LW, RW, LM, RM, LB, RB"""
    wide_positions = {
        Position.LW,
        Position.RW,
        Position.LM,
        Position.RM,
        Position.LB,
        Position.RB,
    }
    wide = [p for p in players if p.position in wide_positions]
    if not wide:
        return None
    weights = [
        math.sqrt(_attr(p, p.attributes.passing.crossing.current, fatigue.get(p, 1.0)))
        * random.uniform(0.7, 1.3)
        for p in wide
    ]
    return random.choices(wide, weights=weights)[0]


def _gk(players: list[Player]) -> Optional[Player]:
    gks = [p for p in players if p.position == Position.GK]
    return gks[0] if gks else None


def _attack_attempt_probability(
    attacker: Player,
    defender: Player,
    fatigue_att: float,
    fatigue_def: float,
) -> float:
    """Can the attacker get past the defender?"""
    att_score = (
        _attr(attacker, attacker.attributes.dribbling.dribbling.current, fatigue_att)
        + _attr(attacker, attacker.attributes.dribbling.agility.current, fatigue_att)
        + _attr(
            attacker, attacker.attributes.dribbling.ballControl.current, fatigue_att
        )
        + _attr(attacker, attacker.attributes.pace.sprintSpeed.current, fatigue_att)
    ) / 4

    def_score = (
        _attr(
            defender, defender.attributes.defending.interceptions.current, fatigue_def
        )
        + _attr(
            defender, defender.attributes.defending.standingTackle.current, fatigue_def
        )
        + _attr(defender, defender.attributes.pace.sprintSpeed.current, fatigue_def)
    ) / 3

    return _normalize(att_score) / (_normalize(att_score) + _normalize(def_score))


def _offside_probability(
    attacker: Player, defender: Player, fatigue_att: float, fatigue_def: float
) -> float:
    """Faster attackers vs slower defenders = higher offside risk."""
    att_pace = _attr(
        attacker, attacker.attributes.pace.sprintSpeed.current, fatigue_att
    )
    def_pace = _attr(
        defender, defender.attributes.pace.sprintSpeed.current, fatigue_def
    )
    # high pace differential increases offside risk
    pace_diff = max(0, att_pace - def_pace)
    return min(0.3, 0.05 + (pace_diff / 100) * 0.25)


def _shot_attempt_probability(
    attacker: Player,
    fatigue_att: float,
    gk: Optional[Player],
) -> float:
    """Did the attack result in a shot?"""
    att_score = (
        _attr(attacker, attacker.attributes.shooting.finishing.current, fatigue_att)
        + _attr(attacker, attacker.attributes.shooting.shotPower.current, fatigue_att)
        + _attr(attacker, attacker.attributes.dribbling.composure.current, fatigue_att)
    ) / 3

    gk_score = 0.0
    if gk:
        gk_score = _attr(gk, gk.attributes.keeping.positioning.current, 1.0) * 0.6

    base = _normalize(att_score)
    gk_modifier = 1.0 - (_normalize(gk_score) * 0.3)
    return max(0.1, min(0.9, base * gk_modifier))


def _long_shot_probability(attacker: Player, fatigue_att: float) -> float:
    return (
        _normalize(
            _attr(attacker, attacker.attributes.shooting.longShots.current, fatigue_att)
        )
        * 0.4
    )


def _shot_on_target_probability(
    attacker: Player,
    fatigue_att: float,
    gk: Optional[Player],
) -> float:
    att_score = (
        _attr(attacker, attacker.attributes.shooting.finishing.current, fatigue_att)
        + _attr(attacker, attacker.attributes.dribbling.composure.current, fatigue_att)
    ) / 2

    gk_score = 0.0
    if gk:
        gk_score = (
            _attr(gk, gk.attributes.keeping.positioning.current, 1.0)
            + _attr(gk, gk.attributes.keeping.reflexes.current, 1.0)
        ) / 2

    att = _normalize(att_score)
    gk = _normalize(gk_score)
    return max(0.1, min(0.85, att / (att + gk * 0.5)))


def _goal_probability(
    attacker: Player,
    fatigue_att: float,
    gk: Optional[Player],
    is_header: bool = False,
) -> float:
    if is_header:
        att_score = (
            _attr(attacker, attacker.attributes.defending.heading.current, fatigue_att)
            + _attr(attacker, attacker.attributes.physical.jumping.current, fatigue_att)
            + _attr(
                attacker, attacker.attributes.dribbling.composure.current, fatigue_att
            )
        ) / 3
    else:
        att_score = (
            _attr(attacker, attacker.attributes.shooting.finishing.current, fatigue_att)
            + _attr(
                attacker, attacker.attributes.shooting.shotPower.current, fatigue_att
            )
            + _attr(
                attacker, attacker.attributes.dribbling.composure.current, fatigue_att
            )
        ) / 3

    gk_score = 0.0
    if gk:
        if is_header:
            gk_score = (
                _attr(gk, gk.attributes.keeping.diving.current, 1.0)
                + _attr(gk, gk.attributes.physical.jumping.current, 1.0)
            ) / 2
        else:
            gk_score = (
                _attr(gk, gk.attributes.keeping.diving.current, 1.0)
                + _attr(gk, gk.attributes.keeping.reflexes.current, 1.0)
                + _attr(gk, gk.attributes.keeping.handling.current, 1.0)
            ) / 3

    att = _normalize(att_score)
    gk = _normalize(gk_score)
    return max(0.05, min(0.7, att / (att + gk)))


def _foul_probability(
    attacker: Player,
    defender: Player,
    fatigue_att: float,
    fatigue_def: float,
) -> float:
    """Failed tackle = foul probability."""
    def_aggression = _attr(
        defender, defender.attributes.physical.aggression.current, fatigue_def
    )
    att_agility = _attr(
        attacker, attacker.attributes.dribbling.agility.current, fatigue_att
    )
    # aggressive defenders fouling agile attackers
    return min(0.7, _normalize(def_aggression) * (1.0 + _normalize(att_agility) * 0.3))


def _card_probability(
    defender: Player, fatigue_def: float, is_second_yellow: bool = False
) -> tuple[float, float]:
    """Returns (yellow_prob, red_prob)."""
    aggression = _attr(
        defender, defender.attributes.physical.aggression.current, fatigue_def
    )
    base = _normalize(aggression)

    if is_second_yellow:
        return 0.0, 0.8  # second yellow = almost certain red

    yellow_prob = min(0.4, base * 0.5)
    red_prob = min(0.02, base * 0.03)
    return yellow_prob, red_prob


def _corner_or_throw(attacker: Player, fatigue_att: float) -> EventType:
    """Determine if a missed shot results in a corner or throw-in."""
    # wide players more likely to generate corners
    wide_positions = {Position.LW, Position.RW, Position.LB, Position.RB}
    if attacker.position in wide_positions:
        return EventType.Corner if _weighted_choice(0.75) else EventType.ThrowIn
    return EventType.Corner if _weighted_choice(0.5) else EventType.ThrowIn


def _header_situation(
    wide: Optional[Player],
    attacker: Player,
    defender: Player,
    fatigue_att: float,
    fatigue_def: float,
) -> bool:
    """Did the cross result in a header situation?"""
    if not wide:
        return False
    cross_quality = _attr(wide, wide.attributes.passing.crossing.current, fatigue_att)
    att_aerial = (
        _attr(attacker, attacker.attributes.defending.heading.current, fatigue_att)
        + _attr(attacker, attacker.attributes.physical.jumping.current, fatigue_att)
    ) / 2
    def_aerial = (
        _attr(defender, defender.attributes.defending.heading.current, fatigue_def)
        + _attr(defender, defender.attributes.physical.jumping.current, fatigue_def)
    ) / 2
    cross_prob = _normalize(cross_quality)
    aerial_prob = _normalize(att_aerial) / (
        _normalize(att_aerial) + _normalize(def_aerial)
    )
    return _weighted_choice(cross_prob * aerial_prob)


# ─── Minute Simulation ───────────────────────────────────────


def _update_fatigue(state: MatchState) -> None:
    for p in state.home_active:
        state.home_fatigue[p] = _fatigue(
            p.attributes.physical.stamina.current, state.minute
        )
    for p in state.away_active:
        state.away_fatigue[p] = _fatigue(
            p.attributes.physical.stamina.current, state.minute
        )


SET_PIECE_NAMES = {
    EventType.Corner: "Corner",
    EventType.ThrowIn: "Throw in",
}


def _simulate_minute(state: MatchState) -> list[MatchEvent]:
    events = []
    minute = state.minute

    # most minutes nothing happens
    if not _weighted_choice(0.5):
        # still update fatigue and check subs even in quiet minutes
        _update_fatigue(state)
        home_sub = _check_substitutions(state, state.home, True)
        away_sub = _check_substitutions(state, state.away, False)
        if home_sub:
            events.append(home_sub)
        if away_sub:
            events.append(away_sub)
        return events

    # determine possession
    home_has_possession = _weighted_choice(_possession_probability(state))
    if home_has_possession:
        state.home_possession_minutes += 1

    attacking_team = state.home if home_has_possession else state.away
    defending_team = state.away if home_has_possession else state.home
    att_active = state.home_active if home_has_possession else state.away_active
    def_active = state.away_active if home_has_possession else state.home_active
    att_fatigue = state.home_fatigue if home_has_possession else state.away_fatigue
    def_fatigue = state.away_fatigue if home_has_possession else state.home_fatigue
    att_cards = state.home_cards if home_has_possession else state.away_cards
    def_cards = state.away_cards if home_has_possession else state.home_cards

    # update fatigue for all active players
    for p in att_active:
        att_fatigue[p] = _fatigue(p.attributes.physical.stamina.current, minute)
    for p in def_active:
        def_fatigue[p] = _fatigue(p.attributes.physical.stamina.current, minute)

    # pick key players
    attacker = _pick_attacker(att_active, att_fatigue)
    midfielder = _pick_midfielder(att_active, att_fatigue)
    defender = _pick_defender(def_active, def_fatigue)
    wide = _pick_wide_player(att_active, att_fatigue)
    gk = _gk(def_active)

    if not attacker or not defender:
        return events

    fatigue_att = att_fatigue.get(attacker, 1.0)
    fatigue_def = def_fatigue.get(defender, 1.0)

    # check substitutions for both teams
    home_sub = _check_substitutions(state, state.home, True)
    away_sub = _check_substitutions(state, state.away, False)
    if home_sub:
        events.append(home_sub)
    if away_sub:
        events.append(away_sub)

    # ── attack attempt ──
    if not _weighted_choice(
        _attack_attempt_probability(attacker, defender, fatigue_att, fatigue_def)
    ):
        # attack broke down — possible throw in
        if _weighted_choice(0.3):
            event_type = EventType.ThrowIn
            if home_has_possession:
                state.away_throw_ins += 1
            else:
                state.home_throw_ins += 1
            events.append(
                MatchEvent(
                    minute=minute,
                    type=event_type,
                    team=defending_team,
                    primary_player=defender,
                    description=f"{minute}' Throw in ({defending_team.name})",
                )
            )
        return events

    # ── offside check ──
    if _weighted_choice(
        _offside_probability(attacker, defender, fatigue_att, fatigue_def)
    ):
        if home_has_possession:
            state.home_offsides += 1
        else:
            state.away_offsides += 1
        events.append(
            MatchEvent(
                minute=minute,
                type=EventType.Offside,
                team=attacking_team,
                primary_player=attacker,
                description=f"{minute}' Offside — {attacker.name.fullName} ({attacking_team.name})",
            )
        )
        return events

    # ── crossing / header situation ──
    is_header = _header_situation(wide, attacker, defender, fatigue_att, fatigue_def)

    # ── shot attempt ──
    if not _weighted_choice(_shot_attempt_probability(attacker, fatigue_att, gk)):
        # no shot — possible foul
        if _weighted_choice(
            _foul_probability(attacker, defender, fatigue_att, fatigue_def)
        ):
            if home_has_possession:
                state.away_fouls += 1
            else:
                state.home_fouls += 1

            yellow_prob, red_prob = _card_probability(
                defender,
                fatigue_def,
                is_second_yellow="yellow" in def_cards.get(defender, []),
            )

            events.append(
                MatchEvent(
                    minute=minute,
                    type=EventType.Foul,
                    team=defending_team,
                    primary_player=defender,
                    secondary_player=attacker,
                    description=f"{minute}' Foul by {defender.name.fullName} on {attacker.name.fullName} ({defending_team.name})",
                )
            )

            if _weighted_choice(red_prob):
                def_cards.setdefault(defender, []).append("red")
                if home_has_possession:
                    state.away_red_cards += 1
                    state.away_red_carded.append(defender)
                else:
                    state.home_red_cards += 1
                    state.home_red_carded.append(defender)
                if defender in def_active:
                    def_active.remove(defender)
                events.append(
                    MatchEvent(
                        minute=minute,
                        type=EventType.RedCard,
                        team=defending_team,
                        primary_player=defender,
                        description=f"{minute}' RED CARD — {defender.name.fullName} ({defending_team.name})",
                    )
                )
            elif _weighted_choice(yellow_prob):
                def_cards.setdefault(defender, []).append("yellow")
                if home_has_possession:
                    state.away_yellow_cards += 1
                else:
                    state.home_yellow_cards += 1
                events.append(
                    MatchEvent(
                        minute=minute,
                        type=EventType.YellowCard,
                        team=defending_team,
                        primary_player=defender,
                        description=f"{minute}' Yellow card — {defender.name.fullName} ({defending_team.name})",
                    )
                )

        return events

    # ── long shot chance ──
    if not is_header and _weighted_choice(
        _long_shot_probability(attacker, fatigue_att)
    ):
        # long shot — lower on target probability
        if home_has_possession:
            state.home_shots += 1
        else:
            state.away_shots += 1
        if not _weighted_choice(0.35):
            set_piece = _corner_or_throw(attacker, fatigue_att)
            if set_piece == EventType.Corner:
                if home_has_possession:
                    state.home_corners += 1
                else:
                    state.away_corners += 1
            else:
                if home_has_possession:
                    state.away_throw_ins += 1
                else:
                    state.home_throw_ins += 1
            events.append(
                MatchEvent(
                    minute=minute,
                    type=set_piece,
                    team=attacking_team,
                    primary_player=attacker,
                    description=f"{minute}' Long shot off target — {attacker.name.fullName}. {SET_PIECE_NAMES[set_piece]} ({attacking_team.name})",
                )
            )
            return events

    # ── shot on target ──
    if home_has_possession:
        state.home_shots += 1
    else:
        state.away_shots += 1

    if not _weighted_choice(_shot_on_target_probability(attacker, fatigue_att, gk)):
        # shot off target
        set_piece = _corner_or_throw(attacker, fatigue_att)
        if set_piece == EventType.Corner:
            if home_has_possession:
                state.home_corners += 1
            else:
                state.away_corners += 1
        else:
            if home_has_possession:
                state.away_throw_ins += 1
            else:
                state.home_throw_ins += 1
        events.append(
            MatchEvent(
                minute=minute,
                type=EventType.ShotOffTarget,
                team=attacking_team,
                primary_player=attacker,
                description=f"{minute}' Shot off target — {attacker.name.fullName} ({attacking_team.name})",
            )
        )
        events.append(
            MatchEvent(
                minute=minute,
                type=set_piece,
                team=attacking_team,
                primary_player=attacker,
                description=f"{minute}' {SET_PIECE_NAMES[set_piece]} ({attacking_team.name})",
            )
        )
        return events

    # shot on target
    if home_has_possession:
        state.home_shots_on_target += 1
    else:
        state.away_shots_on_target += 1

    events.append(
        MatchEvent(
            minute=minute,
            type=EventType.ShotOnTarget,
            team=attacking_team,
            primary_player=attacker,
            description=f"{minute}' Shot on target — {attacker.name.fullName} ({attacking_team.name})",
        )
    )

    # ── goal ──
    if _weighted_choice(
        _goal_probability(attacker, fatigue_att, gk, is_header=is_header)
    ):
        if home_has_possession:
            state.home_score += 1
        else:
            state.away_score += 1

        assist_player = None
        assist_str = ""
        if is_header and wide and wide != attacker:
            assist_player = wide
            assist_str = f" (assist: {wide.name.fullName})"
        elif midfielder and midfielder != attacker and _weighted_choice(0.7):
            assist_player = midfielder
            assist_str = f" (assist: {midfielder.name.fullName})"

        goal_type = "Header" if is_header else "GOAL"
        events.append(
            MatchEvent(
                minute=minute,
                type=EventType.Goal,
                team=attacking_team,
                primary_player=attacker,
                secondary_player=assist_player,
                description=f"{minute}' {goal_type} — {attacker.name.fullName}{assist_str} ({attacking_team.name})",
            )
        )
    else:
        # saved — corner or throw
        handling = gk.attributes.keeping.handling.current if gk else 50
        is_caught = _weighted_choice(handling * 0.5 / 100)
        if not is_caught:
            set_piece = EventType.Corner
            if home_has_possession:
                state.home_corners += 1
            else:
                state.away_corners += 1
            events.append(
                MatchEvent(
                    minute=minute,
                    type=EventType.Corner,
                    team=attacking_team,
                    primary_player=attacker,
                    description=f"{minute}' Corner ({attacking_team.name})",
                )
            )

        save_str = "Save" if is_caught else "Save — parried to corner"
        events.append(
            MatchEvent(
                minute=minute,
                type=EventType.Save,
                team=defending_team,
                primary_player=gk,
                secondary_player=attacker,
                description=f"{minute}' {save_str} — {gk.name.fullName} ({defending_team.name})",
            )
        )

    return events


# ─── Main Simulation ─────────────────────────────────────────


def simulate(home: Team, away: Team) -> MatchState:
    state = MatchState(home=home, away=away)
    state.stoppage_time = random.randint(1, 5)  # rough initial estimate

    for minute in range(1, 91):
        state.minute = minute
        events = _simulate_minute(state)
        state.events.extend(events)

    # stoppage time
    state.stoppage_time = _calculate_stoppage(state)
    for minute in range(91, 91 + state.stoppage_time):
        state.minute = minute
        events = _simulate_minute(state)
        state.events.extend(events)

    return state
