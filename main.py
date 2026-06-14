from player import Player

if __name__ == "__main__":
    for i in range(5):
        player = Player.random()
        player.display()
        print("\n" + "─" * 40 + "\n")

# from formations import ALL_FORMATIONS

# for f in ALL_FORMATIONS:
#     print(f"{f.name:<20} def: {f.defensiveness:.1f}  off: {f.offensiveness:.1f}")

# from team import Team

# if __name__ == "__main__":
#     for i in range(3):
#         team = Team.random()
#         team.display()
#         print("\n" + "─" * 40 + "\n")

# from match_engine import simulate
# from match_report import print_report
# from team import Team

# if __name__ == "__main__":
#     home = Team.random()
#     away = Team.random()
#     state = simulate(home, away)
#     print_report(state)

# from match_engine import simulate
# from team import Team

# if __name__ == "__main__":
#     for i in range(20):
#         home = Team.random()
#         away = Team.random()
#         state = simulate(home, away)
#         print(f"{home.name} vs {away.name}: {state.home_score} - {state.away_score}")
