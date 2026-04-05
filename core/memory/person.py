"""Helpers for reading general person data from Football Manager memory."""

from core.memory.process import follow_pointer_chain, read_c_string, read_uint

CURRENT_DAY_RVA = 0x631D5BC
CURRENT_YEAR_RVA = 0x631D5BE
PERSON_UID_OFFSET = 0x0C
PERSON_BIRTH_DAY_OFFSET = 0x44
PERSON_BIRTH_YEAR_OFFSET = 0x46


def read_person_name(process, person_address):
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


def read_person_age(process, person_address, fm_base_address):
    birth_day = read_uint(process, person_address + PERSON_BIRTH_DAY_OFFSET, 2)
    birth_year = read_uint(process, person_address + PERSON_BIRTH_YEAR_OFFSET, 2)
    current_day = read_uint(process, fm_base_address + CURRENT_DAY_RVA, 2) & 0x1FF
    current_year = read_uint(process, fm_base_address + CURRENT_YEAR_RVA, 2)
    return current_year - birth_year - 1 + int(birth_day <= current_day)
