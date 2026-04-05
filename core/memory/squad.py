"""Read squad CA and PA data directly from Football Manager's process memory."""

import pandas as pd

from core.memory.person import read_person_name
from core.memory.players import PERSON_OBJECT_OFFSET, PLAYER_OBJECT_VTABLE
from core.memory.process import open_fm_process, read_uint
from core.memory.session import find_manager_address, find_ptr_root_target, get_current_club_address, read_game_root_state


def load_squad_table(target_teams=(22,), process=None):
    process = process or open_fm_process()
    target_teams = {target_teams} if isinstance(target_teams, int) else set(target_teams)

    club_address = get_current_club_address(process)
    team_list_start = read_uint(process, club_address + 0x18)
    team_list_end = read_uint(process, club_address + 0x20)
    rows = []

    for team_slot in range(team_list_start, team_list_end, 8):
        team_address = read_uint(process, team_slot)
        if not team_address or read_uint(process, team_address + 0x28, 1) not in target_teams:
            continue

        player_list_start = read_uint(process, team_address + 0x38)
        player_list_end = read_uint(process, team_address + 0x40)
        for player_slot in range(player_list_start, player_list_end, 8):
            player_address = read_uint(process, player_slot)
            if not player_address or read_uint(process, player_address) != PLAYER_OBJECT_VTABLE:
                continue

            rows.append(
                [
                    read_person_name(process, player_address + PERSON_OBJECT_OFFSET),
                    read_uint(process, player_address + 0x200, 2),
                    read_uint(process, player_address + 0x202, 2),
                ]
            )

    if not rows:
        return pd.DataFrame(columns=["Name", "CA", "PA"])

    df = pd.DataFrame(rows, columns=["Name", "CA", "PA"])
    return df.sort_values(by=["PA", "CA"], ascending=[False, False]).reset_index(drop=True)
