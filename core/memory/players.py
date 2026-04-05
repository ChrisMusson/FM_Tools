"""Helpers for finding and reading player data from Football Manager memory."""

import pandas as pd

from core.memory.cache import get_cached_or_compute
from core.memory.person import PERSON_UID_OFFSET, read_person_name
from core.memory.process import iter_pattern_matches, read_uint
from core.scouting.players.attributes import SCAN_ATTRIBUTES

PLAYER_OBJECT_VTABLE = 0x145A4E958
PERSON_OBJECT_OFFSET = 0x278
PLAYER_OBJECT_SCAN_PATTERN = b"\x78\xee\xa4\x45\x01"
PLAYER_CA_OFFSET = 0x200
PLAYER_PA_OFFSET = 0x202
PLAYER_VALUE_OFFSET = 0x1D0
PLAYER_ATTRIBUTE_OFFSET = 0x217
EMPTY_PLAYER_SNAPSHOT = {"Memory Name": None, "CA": None, "PA": None, "Value": None, **{attribute.value: None for attribute in SCAN_ATTRIBUTES}}
_PLAYER_PROCESS_CACHE = {}


def _get_player_process_cache(process):
    process_key = getattr(process, "pid", None) or getattr(process, "process_id", None) or id(process)
    cache = _PLAYER_PROCESS_CACHE.get(process_key)
    if cache is None:
        cache = {}
        _PLAYER_PROCESS_CACHE[process_key] = cache
    return cache


def scan_player_person_addresses(process, *, refresh=False):
    cache = _get_player_process_cache(process)
    if not refresh and "person_addresses" in cache:
        return cache["person_addresses"]

    def build_person_addresses():
        people = {}

        for person_address in iter_pattern_matches(process, PLAYER_OBJECT_SCAN_PATTERN, writable=True, executable=False, private=True):
            try:
                uid = read_uint(process, person_address + PERSON_UID_OFFSET, 4)
            except Exception:
                continue
            if uid > 0:
                people[uid] = person_address

        return people

    person_addresses, _cache_hit = get_cached_or_compute(process, "player_person_addresses", key_parts={}, builder=build_person_addresses, refresh=refresh)
    cache["person_addresses"] = person_addresses
    return person_addresses


def read_player_snapshot(process, person_address):
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


def build_shortlist_player_table(shortlist_df, process):
    ordered_uids = [None if pd.isna(uid) else int(uid) for uid in shortlist_df["UID"].astype("Int64")]

    def build_rows():
        person_addresses = scan_player_person_addresses(process)
        rows = []

        for uid_int in ordered_uids:
            snapshot = read_player_snapshot(process, person_addresses.get(uid_int))
            rows.append({"UID": uid_int, **snapshot})

        return rows

    rows, _cache_hit = get_cached_or_compute(process, "player_shortlist_rows", key_parts={"uids": ordered_uids}, builder=build_rows)

    return pd.DataFrame(rows).astype({"UID": "Int64"})
