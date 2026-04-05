"""Helpers for resolving live Football Manager world pointers and cache fingerprints."""

import struct

from core.memory.person import CURRENT_DAY_RVA, CURRENT_YEAR_RVA, PERSON_UID_OFFSET
from core.memory.process import follow_pointer_chain, get_fm_base_address, get_fm_image_range, open_fm_process, read_uint

PTR_ROOT_PREFIX = b"\x48\x8b\x35"
PTR_ROOT_SUFFIX = b"\x48\x8b\x56\x18\x4c\x8b\x76\x20\x49\x29\xd6\xb0\x01\x49\x83\xfe\x10"
PTR_ROOT_PATTERN_LENGTH = 24


def _iter_ptr_root_instructions(process, start_address, end_address, chunk_size=0x200000):
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


def _resolve_manager_address_from_ptr_root(process, ptr_root):
    return follow_pointer_chain(process, ptr_root + 0x18, 0x0, 0x0, 0x58, 0x128)


def find_ptr_root_target(process=None):
    process = process or open_fm_process()
    scan_start, scan_end = get_fm_image_range(process)

    for instruction in _iter_ptr_root_instructions(process, scan_start, scan_end):
        try:
            displacement = struct.unpack("<i", process.read_bytes(instruction + 3, 4))[0]
            ptr_root_target = instruction + 7 + displacement
            ptr_root = read_uint(process, ptr_root_target)
            manager_address = _resolve_manager_address_from_ptr_root(process, ptr_root)
            if manager_address:
                return ptr_root_target
        except Exception:
            continue

    raise RuntimeError("Could not resolve the ptr_root target for the current save state inside fm.exe")


def find_manager_address(process=None):
    process = process or open_fm_process()
    ptr_root_target = find_ptr_root_target(process)
    ptr_root = read_uint(process, ptr_root_target)
    manager_address = _resolve_manager_address_from_ptr_root(process, ptr_root)
    if manager_address:
        return manager_address
    raise RuntimeError("Resolved the ptr_root target, but the manager chain did not return a valid address")


def get_current_club_address(process=None):
    process = process or open_fm_process()
    manager_address = find_manager_address(process)
    club_address = follow_pointer_chain(process, manager_address, 0xC8, 0x10, 0x30)
    if not club_address:
        raise RuntimeError("Resolved the manager address, but the club chain returned null")
    return club_address


def read_game_root_state(process=None, *, ptr_root_target=None, target_team=22):
    process = process or open_fm_process()
    ptr_root_target = ptr_root_target if ptr_root_target is not None else find_ptr_root_target(process)

    ptr_root = read_uint(process, ptr_root_target)
    manager_address = _resolve_manager_address_from_ptr_root(process, ptr_root)
    if not manager_address:
        raise RuntimeError("Resolved the ptr_root target, but the manager chain returned null")

    club_address = follow_pointer_chain(process, manager_address, 0xC8, 0x10, 0x30)
    if not club_address:
        raise RuntimeError("Resolved the manager address, but the club chain returned null")

    team_list_start = read_uint(process, club_address + 0x18)
    team_list_end = read_uint(process, club_address + 0x20)
    target_team_address = None
    target_player_list_start = None
    target_player_list_end = None

    if target_team is not None:
        for team_slot in range(team_list_start, team_list_end, 8):
            team_address = read_uint(process, team_slot)
            if not team_address or read_uint(process, team_address + 0x28, 1) != target_team:
                continue

            target_team_address = team_address
            target_player_list_start = read_uint(process, team_address + 0x38)
            target_player_list_end = read_uint(process, team_address + 0x40)
            break

    fm_base_address = get_fm_base_address(process)
    current_day = read_uint(process, fm_base_address + CURRENT_DAY_RVA, 2) & 0x1FF
    current_year = read_uint(process, fm_base_address + CURRENT_YEAR_RVA, 2)

    return {
        "ptr_root_target": ptr_root_target,
        "ptr_root": ptr_root,
        "manager_address": manager_address,
        "manager_uid": read_uint(process, manager_address + PERSON_UID_OFFSET, 4),
        "club_address": club_address,
        "team_list_start": team_list_start,
        "team_list_end": team_list_end,
        "target_team": target_team,
        "target_team_address": target_team_address,
        "target_player_list_start": target_player_list_start,
        "target_player_list_end": target_player_list_end,
        "current_day": current_day,
        "current_year": current_year,
    }


def read_game_cache_fingerprint(process=None):
    process = process or open_fm_process()
    process_id = getattr(process, "pid", None) or getattr(process, "process_id", None) or 0
    fm_base_address = get_fm_base_address(process)
    state = read_game_root_state(process, target_team=None)

    return (
        int(process_id),
        int(fm_base_address),
        int(state["ptr_root_target"]),
        int(state["ptr_root"]),
        int(state["manager_uid"]),
        int(state["manager_address"]),
        int(state["club_address"]),
        int(state["team_list_start"]),
        int(state["team_list_end"]),
    )
