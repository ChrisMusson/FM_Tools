from core.squad_data import load_squad_table

squad_types = {
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

"""Example: Print the Name, CA, and PA of players in the first team and reserves of your manager's club"""
squad_ids = [0, 1]  # First team and reserves
players = load_squad_table(target_teams=squad_ids).reset_index(drop=True).head(10)
print(players.head(10))
