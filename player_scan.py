import re

import pandas as pd
from core.fm_process import open_fm_process
from core.html_report import build_sortable_table_html
from core.player_memory import build_shortlist_player_table, format_currency
from core.role_scoring import filter_players_for_roles, score_players_for_roles
from core.roles import ROLE


SHORTLIST_PATH = "shortlist.html"
OUTPUT_PATH = "table.html"
EXTRA_COLUMNS = [
    "Value",
    "CA",
    "PA",
]
ROLES = [
    ROLE.SWEEPER_KEEPER.DEFEND,
    ROLE.FULL_BACK.ATTACK,
    ROLE.INVERTED_WING_BACK.ATTACK,
    ROLE.BALL_PLAYING_DEFENDER.DEFEND,
    ROLE.DEFENSIVE_MIDFIELDER.SUPPORT,
    ROLE.SEGUNDO_VOLANTE.ATTACK,
    ROLE.WINGER.SUPPORT,
    ROLE.INSIDE_FORWARD.SUPPORT,
    ROLE.PRESSING_FORWARD.SUPPORT,
    ROLE.ADVANCED_FORWARD.ATTACK
]
TARGET_PLAYER_COUNT = 2000


def load_shortlist_table(path: str = SHORTLIST_PATH):
    players_df = pd.read_html(path, encoding="utf-8")[0].dropna(how="all")
    players_df = players_df[players_df.columns[2:]]
    if "UID" not in players_df.columns:
        raise ValueError("shortlist.html must include a UID column in the exported player search view")
    players_df["UID"] = players_df["UID"].astype("Int64")
    return players_df


def parse_money_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip().lower().replace(",", "")
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([kmb])?", text)
    if not match:
        return None

    amount = float(match.group(1))
    multiplier = {"k": 10**3, "m": 10**6, "b": 10**9}.get(match.group(2), 1)
    return int(amount * multiplier)


def main():
    process = open_fm_process()
    players_df = load_shortlist_table()
    players_df = players_df.merge(build_shortlist_player_table(players_df, process), on="UID")
    players_df = score_players_for_roles(players_df, ROLES)
    players_df = filter_players_for_roles(players_df, ROLES, target_n=TARGET_PLAYER_COUNT, filter_type="roles")
    value_sort_values = players_df["Value"].astype("Int64").tolist()
    wage_sort_values = players_df["Wage"].apply(parse_money_text).tolist() if "Wage" in players_df.columns else None
    players_df["Value"] = players_df["Value"].apply(format_currency)
    role_columns = [role.short_label for role in ROLES]
    players_df = players_df.rename(columns={role.code: role.short_label for role in ROLES})

    name_col = next((column for column in ["Name", "Player", "Memory Name"] if column in players_df.columns), None)
    if name_col == "Memory Name":
        players_df = players_df.rename(columns={"Memory Name": "Name"})
        name_col = "Name"
    if name_col in {"Name", "Player"}:
        players_df[name_col] = players_df[name_col].str.replace(" - Pick Player", "")

    base_columns = [column for column in ["Nat", "Club", "Wage", "Age", name_col, "Position"] if column and column in players_df.columns]
    extra_columns = [column for column in EXTRA_COLUMNS if column in players_df.columns]
    players_df = players_df[base_columns + extra_columns + role_columns]

    for col in ["Age", "CA", "PA"]:
        if col in players_df.columns:
            players_df[col] = players_df[col].astype("Int64")

    # players_df = players_df.loc[players_df["PA"] >= 150]
    # players_df = players_df.loc[players_df["Age"] <= 18]
    # players_df = players_df.drop("PA", axis=1)

    html = build_sortable_table_html(
        players_df,
        title="FM Player Scan",
        subtitle=f"{len(players_df):,} shortlisted players scored across {len(ROLES)} selected roles.",
        roles=ROLES,
        score_columns=role_columns,
        default_sort_column="Value",
        column_sort_values={"Value": value_sort_values, **({"Wage": wage_sort_values} if wage_sort_values is not None else {})},
    )
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
