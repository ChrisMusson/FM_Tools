"""Reload intake day until the generated players hit the chosen CA and PA targets."""

from time import sleep

from core.squad_data import load_squad_table, open_fm_process
from core.ui_automation import create_input_controller, reload_last_save, wait_for_continue_button

ACTION_PAUSE_SECONDS = 2
TARGET_TEAM_IDS = [22]
MINIMUM_TARGET_PA = 140
MINIMUM_TARGET_CA = 114


def main():
    controller = create_input_controller(action_pause=ACTION_PAUSE_SECONDS)
    process = open_fm_process()
    reload_last_save(controller)
    trial = 0

    while True:
        trial += 1
        controller.press("space")
        controller.press("escape")
        wait_for_continue_button()

        sleep(1)
        squad = load_squad_table(target_teams=TARGET_TEAM_IDS, process=process)
        squad = squad.sort_values(by=["PA", "CA"], ascending=[False, False])

        max_pa = squad["PA"].max()
        max_ca = squad["CA"].max()

        print(f"\nTrial {trial}")
        print(squad.head(3))

        if max_pa < MINIMUM_TARGET_PA or max_ca < MINIMUM_TARGET_CA:
            reload_last_save(controller)
            continue

        top_targets = squad.loc[(squad["PA"] >= MINIMUM_TARGET_PA) & (squad["CA"] >= MINIMUM_TARGET_CA)]
        nearby_high_potential = squad.loc[squad["PA"] >= MINIMUM_TARGET_PA - 20]
        if len(top_targets) >= 1 and len(nearby_high_potential) >= 1:
            print(squad)
            return

        reload_last_save(controller)


if __name__ == "__main__":
    main()
