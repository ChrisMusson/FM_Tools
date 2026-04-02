import os
from time import sleep

import pandas as pd

from core.squad_data import load_squad_table, open_fm_process
from core.ui_automation import InputController, advance_one_day, reload_last_save

START_DELAY_SECONDS = 3  # how long you have from running the script to make the FM24 window active
ACTION_PAUSE_SECONDS = 1  # how long to wait between actions (mouse clicks, key presses, etc.)

CA_TARGET = 120
PA_TARGET = 190


def should_stop_intake_loop(players_df):
    # stop if there is a player whose (CA >= CA_TARGET) and (PA >= PA_TARGET)
    return not players_df.loc[(players_df["CA"] >= CA_TARGET) & (players_df["PA"] >= PA_TARGET)].empty


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    controller = InputController(action_pause=ACTION_PAUSE_SECONDS)
    process = open_fm_process()
    best_players_by_trial = []
    reload_last_save(controller)
    trial = 0

    while True:
        try:
            trial += 1
            advance_one_day(controller)

            players_df = load_squad_table(process=process)
            best_player = players_df.sort_values(by=["PA", "CA"], ascending=[False, False]).iloc[0]
            best_players_by_trial.append(
                {
                    "Trial": trial,
                    "Name": best_player["Name"],
                    "CA": best_player["CA"],
                    "PA": best_player["PA"],
                }
            )

            leaderboard = (
                pd.DataFrame(best_players_by_trial)
                .assign(Total=lambda df: df["CA"] + df["PA"])
                .sort_values(by=["Total", "PA", "CA", "Trial"], ascending=[False, False, False, True])
                .head(10)
                .drop(columns=["Total"])
                .reset_index(drop=True)
            )
            latest_trial = best_players_by_trial[-1]
            clear_terminal()
            print(leaderboard)
            print()
            print(f"Latest trial: {latest_trial['Trial']} | {latest_trial['Name']} | CA {latest_trial['CA']} | PA {latest_trial['PA']}")
            print()

            if should_stop_intake_loop(players_df):
                return

            reload_last_save(controller)

        except Exception as exc:
            print(exc)
            reload_last_save(controller)


if __name__ == "__main__":
    sleep(START_DELAY_SECONDS)
    main()
