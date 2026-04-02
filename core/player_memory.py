"""Helpers for finding and reading player data from Football Manager memory."""

import pandas as pd

from core.attributes import SCAN_ATTRIBUTES
from core.fm_process import follow_pointer_chain, iter_pattern_matches, read_c_string, read_uint

PLAYER_OBJECT_VTABLE = 0x145A4E958
PERSON_OBJECT_OFFSET = 0x278
PERSON_UID_OFFSET = 0x0C
PERSON_SCAN_PATTERN = b"\x78\xee\xa4\x45\x01"
PLAYER_CA_OFFSET = 0x200
PLAYER_PA_OFFSET = 0x202
PLAYER_VALUE_OFFSET = 0x1D0
PLAYER_ATTRIBUTE_OFFSET = 0x217
EMPTY_PLAYER_SNAPSHOT = {"Memory Name": None, "CA": None, "PA": None, "Value": None, **{attribute.value: None for attribute in SCAN_ATTRIBUTES}}


def read_person_name(process, person_address: int | None) -> str | None:
    if person_address is None:
        return None

    try:
        common_name = follow_pointer_chain(process, person_address, 0x68, 0x0)
        if common_name:
            return read_c_string(process, common_name + 0x4, 100)

        first_name = follow_pointer_chain(process, person_address, 0x58, 0x0)
        last_name = follow_pointer_chain(process, person_address, 0x60, 0x0)
        if first_name and last_name:
            return f"{read_c_string(process, first_name + 0x4, 50)} {read_c_string(process, last_name + 0x4, 50)}"

        full_name = read_uint(process, person_address + 0x48)
        if full_name:
            return read_c_string(process, full_name + 0x4, 255)
    except Exception:
        return None

    return None


def scan_person_addresses(process) -> dict[int, int]:
    people: dict[int, int] = {}

    for person_address in iter_pattern_matches(process, PERSON_SCAN_PATTERN, writable=True, executable=False, private=True):
        try:
            uid = read_uint(process, person_address + PERSON_UID_OFFSET, 4)
        except Exception:
            continue
        if uid > 0:
            people[uid] = person_address

    return people


def read_player_snapshot(process, person_address: int | None) -> dict[str, int | None]:
    if person_address is None:
        return EMPTY_PLAYER_SNAPSHOT.copy()

    try:
        player_address = person_address - PERSON_OBJECT_OFFSET
        attributes = list(process.read_bytes(player_address + PLAYER_ATTRIBUTE_OFFSET, len(SCAN_ATTRIBUTES)))
        return {
            "Memory Name": read_person_name(process, person_address),
            "CA": read_uint(process, player_address + PLAYER_CA_OFFSET, 2),
            "PA": read_uint(process, player_address + PLAYER_PA_OFFSET, 2),
            "Value": read_uint(process, player_address + PLAYER_VALUE_OFFSET, 4),
            **{attribute.value: int(value) for attribute, value in zip(SCAN_ATTRIBUTES, attributes, strict=True)},
        }
    except Exception:
        return EMPTY_PLAYER_SNAPSHOT.copy()


def build_shortlist_player_table(shortlist_df: pd.DataFrame, process) -> pd.DataFrame:
    person_addresses = scan_person_addresses(process)
    rows = []

    for uid in shortlist_df["UID"].astype("Int64"):
        uid_int = None if pd.isna(uid) else int(uid)
        snapshot = read_player_snapshot(process, person_addresses.get(uid_int))
        rows.append({"UID": uid_int, **snapshot})

    return pd.DataFrame(rows).astype({"UID": "Int64"})


def format_currency(value):
    if pd.isna(value):
        return "-"
    if value >= 10**6:
        return f"£{round(value / 10**6, 1)}m"
    if value >= 10**3:
        return f"£{int(value / 10**3)}k"
    if value >= 0:
        return f"£{int(value)}"
    return "-"
