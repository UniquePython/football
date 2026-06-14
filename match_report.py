from match_state import MatchState
from player import Player
from position import Position

POSITION_ORDER = [
    Position.GK,
    Position.LB,
    Position.CB,
    Position.RB,
    Position.CDM,
    Position.LM,
    Position.CM,
    Position.RM,
    Position.CAM,
    Position.LW,
    Position.RW,
    Position.ST,
]


def _sort_players(players: list[Player]) -> list[Player]:
    return sorted(
        players,
        key=lambda p: (
            POSITION_ORDER.index(p.position) if p.position in POSITION_ORDER else 99
        ),
    )


def print_report(state: MatchState) -> None:
    home = state.home
    away = state.away

    # ── Header ──
    print("=" * 60)
    print(f"  {home.name} vs {away.name}")
    print(f"  {home.country.capitalize()} | {home.formation} vs {away.formation}")
    print("=" * 60)

    # ── Final Score ──
    print(f"\n  FULL TIME: {state.score_str}")
    print(f"  {90 + state.stoppage_time}' played ({state.stoppage_time}' stoppage)\n")

    # ── Match Events ──
    print("─" * 60)
    print("  MATCH EVENTS")
    print("─" * 60)
    for event in state.events:
        print(f"  {event.description}")

    # ── Match Stats ──
    print("\n" + "─" * 60)
    print("  MATCH STATS")
    print("─" * 60)
    print(f"  {'':30} {home.name[:12]:>12}  {away.name[:12]:>12}")
    print(
        f"  {'Possession':<30} {state.home_possession*100:>11.0f}%  {(1-state.home_possession)*100:>11.0f}%"
    )
    print(f"  {'Shots':<30} {state.home_shots:>12}  {state.away_shots:>12}")
    print(
        f"  {'Shots on Target':<30} {state.home_shots_on_target:>12}  {state.away_shots_on_target:>12}"
    )
    print(f"  {'Corners':<30} {state.home_corners:>12}  {state.away_corners:>12}")
    print(f"  {'Fouls':<30} {state.home_fouls:>12}  {state.away_fouls:>12}")
    print(
        f"  {'Yellow Cards':<30} {state.home_yellow_cards:>12}  {state.away_yellow_cards:>12}"
    )
    print(f"  {'Red Cards':<30} {state.home_red_cards:>12}  {state.away_red_cards:>12}")
    print(f"  {'Offsides':<30} {state.home_offsides:>12}  {state.away_offsides:>12}")
    print(f"  {'Throw ins':<30} {state.home_throw_ins:>12}  {state.away_throw_ins:>12}")

    # ── Lineups ──
    print("\n" + "─" * 60)
    print("  LINEUPS")
    print("─" * 60)
    print(f"\n  {home.name} ({home.formation})")
    for p in _sort_players(state.home_active):
        cards = state.home_cards.get(p, [])
        card_str = " [Y]" if cards.count("yellow") == 1 else ""
        print(
            f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall}{card_str}"
        )
    for p in state.home_red_carded:
        print(
            f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall} [R] (sent off)"
        )

    print(f"\n  {away.name} ({away.formation})")
    for p in _sort_players(state.away_active):
        cards = state.away_cards.get(p, [])
        card_str = " [Y]" if cards.count("yellow") == 1 else ""
        print(
            f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall}{card_str}"
        )
    for p in state.away_red_carded:
        print(
            f"    {p.position.upper():<5} {p.name.fullName:<25} OVR {p.overall} [R] (sent off)"
        )

    print("\n" + "=" * 60)
