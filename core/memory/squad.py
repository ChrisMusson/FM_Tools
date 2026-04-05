"""Read squad CA and PA data directly from Football Manager's process memory."""

import struct

import pandas as pd

from core.memory.person import read_person_name
from core.memory.players import PERSON_OBJECT_OFFSET, PLAYER_OBJECT_VTABLE
from core.memory.process import follow_pointer_chain, get_fm_image_range, open_fm_process, read_uint

PTR_ROOT_PREFIX = b"\x48\x8b\x35"
PTR_ROOT_SUFFIX = b"\x48\x8b\x56\x18\x4c\x8b\x76\x20\x49\x29\xd6\xb0\x01\x49\x83\xfe\x10"
PTR_ROOT_PATTERN_LENGTH = 24


def _iter_ptr_root_instructions(process, start_address: int, end_address: int, chunk_size: int = 0x200000):
    address = start_address
    overlap = PTR_ROOT_PATTERN_LENGTH - 1
    carry = b""

    while address < end_address:
        size = min(chunk_size, end_address - address)
        data = carry + process.read_bytes(address, size)
        base = address - len(carry)
        search_from = 0

        while True:
            suffix_index = data.find(PTR_ROOT_SUFFIX, search_from)
            if suffix_index == -1:
                break

            pattern_start = suffix_index - 7
            if 0 <= pattern_start <= len(data) - PTR_ROOT_PATTERN_LENGTH:
                if data[pattern_start : pattern_start + len(PTR_ROOT_PREFIX)] == PTR_ROOT_PREFIX:
                    yield base + pattern_start

            search_from = suffix_index + 1

        carry = data[-overlap:]
        address += size


def find_manager_address(process=None) -> int:
    process = process or open_fm_process()
    scan_start, scan_end = get_fm_image_range(process)

    for instruction in _iter_ptr_root_instructions(process, scan_start, scan_end):
        try:
            displacement = struct.unpack("<i", process.read_bytes(instruction + 3, 4))[0]
            ptr_root_target = instruction + 7 + displacement
            ptr_root = read_uint(process, ptr_root_target)
            manager_address = follow_pointer_chain(process, ptr_root + 0x18, 0x0, 0x0, 0x58, 0x128)
            if manager_address:
                return manager_address
        except Exception:
            continue

    raise RuntimeError("Could not resolve a valid manager address from the ptr_root signature inside fm.exe")


def get_current_club_address(process=None) -> int:
    process = process or open_fm_process()
    manager_address = find_manager_address(process)
    club_address = follow_pointer_chain(process, manager_address, 0xC8, 0x10, 0x30)
    if not club_address:
        raise RuntimeError("Resolved the manager address, but the club chain returned null")
    return club_address


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
