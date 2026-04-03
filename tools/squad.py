"""Example script for printing Name, CA, and PA from selected squad buckets."""

from core.memory.squad import load_squad_table

SQUAD_TYPES = {
    0: "First Team",
    1: "Reserves",
    2: "A",
    3: "B",
    4: "Superdraft A",
    5: "Superdraft B",
    6: "Superdraft C",
    7: "Superdraft D",
    8: "Waivers",
    9: "U23",
    10: "U21",
    11: "U19",
    12: "U18",
    13: "C",
    14: "Amateur",
    15: "II",
    16: "Team 2",
    17: "Team 3",
    18: "U20",
    22: "Youth Evaluation",
    30: "Dutch Reserves",
    44: "Second Team",
}


def main():
    squad_ids = [0, 9, 22]
    players = load_squad_table(target_teams=squad_ids).reset_index(drop=True)
    print(players.head(10))


if __name__ == "__main__":
    main()
