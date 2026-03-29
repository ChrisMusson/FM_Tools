"""Read squad CA and PA data directly from Football Manager's process memory."""

import ctypes
import ctypes.util
import struct
from pathlib import Path

import pandas as pd
from core.platform_support import IS_LINUX, IS_WINDOWS

PLAYER_VTABLE = 0x145A4E958
FM_EXE_PATH_FRAGMENT = "/Football Manager 2024/fm.exe"
PTR_ROOT_PREFIX = b"\x48\x8b\x35"
PTR_ROOT_SUFFIX = b"\x48\x8b\x56\x18\x4c\x8b\x76\x20\x49\x29\xd6\xb0\x01\x49\x83\xfe\x10"
PTR_ROOT_PATTERN_LENGTH = 24


class IOVec(ctypes.Structure):
    _fields_ = [("iov_base", ctypes.c_void_p), ("iov_len", ctypes.c_size_t)]


class LinuxFmProcess:
    def __init__(self, pid: int):
        self.pid = pid
        libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        self._readv = libc.process_vm_readv
        self._readv.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(IOVec),
            ctypes.c_ulong,
            ctypes.POINTER(IOVec),
            ctypes.c_ulong,
            ctypes.c_ulong,
        ]
        self._readv.restype = ctypes.c_ssize_t
        self.fm_text_start, self.fm_text_end = self._find_text_range()

    @classmethod
    def open(cls) -> "LinuxFmProcess":
        return cls(_find_linux_fm_pid())

    def _find_text_range(self) -> tuple[int, int]:
        with Path(f"/proc/{self.pid}/maps").open() as fh:
            regions = []
            for line in fh:
                parts = line.split(maxsplit=5)
                start_s, end_s = parts[0].split("-")
                perms = parts[1]
                path = parts[5].strip() if len(parts) > 5 else ""
                regions.append((int(start_s, 16), int(end_s, 16), perms, path))

        marker_index = next(
            (index for index, (_, _, _, path) in enumerate(regions) if FM_EXE_PATH_FRAGMENT in path or path.endswith("/fm.exe")),
            None,
        )
        if marker_index is None:
            raise RuntimeError("Could not find any fm.exe memory mappings")

        current_end = regions[marker_index][1]
        for start, end, perms, _ in regions[marker_index:]:
            if start > current_end:
                break
            current_end = max(current_end, end)
            if "x" in perms:
                return start, end

        raise RuntimeError("Could not find an executable fm.exe memory range")

    def read_bytes(self, address: int, size: int) -> bytes:
        buffer = ctypes.create_string_buffer(size)
        local = IOVec(ctypes.cast(buffer, ctypes.c_void_p), size)
        remote = IOVec(ctypes.c_void_p(address), size)
        bytes_read = self._readv(self.pid, ctypes.byref(local), 1, ctypes.byref(remote), 1, 0)
        if bytes_read != size:
            err = ctypes.get_errno()
            raise OSError(err, f"process_vm_readv returned {bytes_read} bytes, expected {size}")
        return bytes(buffer.raw)


def _find_linux_fm_pid() -> int:
    for proc_dir in Path("/proc").iterdir():
        if not proc_dir.name.isdigit():
            continue
        try:
            text = (proc_dir / "maps").read_text()
        except Exception:
            continue
        if FM_EXE_PATH_FRAGMENT in text or text.rstrip().endswith("/fm.exe"):
            return int(proc_dir.name)
    raise RuntimeError("Could not find a live process with Football Manager's fm.exe mapped")


def _get_windows_fm_image_range(process) -> tuple[int, int]:
    import pymem.process

    module = pymem.process.module_from_name(process.process_handle, "fm.exe")
    if module is None:
        raise RuntimeError("Could not find fm.exe in the target process module list")

    base_address = int(module.lpBaseOfDll)
    image_size = int(module.SizeOfImage)
    return base_address, base_address + image_size


def read_uint(process, address: int, size: int = 8) -> int:
    return int.from_bytes(process.read_bytes(address, size), byteorder="little")


def read_c_string(process, address: int, size: int) -> str:
    raw = process.read_bytes(address, size).split(b"\x00", 1)[0]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def follow_pointer_chain(process, base_address: int, *offsets: int) -> int | None:
    current = base_address
    for offset in offsets:
        current = read_uint(process, current + offset)
        if current == 0:
            return None
    return current


def read_player_name(process, name_base: int | None) -> str | None:
    if name_base is None:
        return None

    try:
        common_name = follow_pointer_chain(process, name_base, 0x68, 0x0)
        if common_name:
            return read_c_string(process, common_name + 0x4, 100)

        first_name = follow_pointer_chain(process, name_base, 0x58, 0x0)
        last_name = follow_pointer_chain(process, name_base, 0x60, 0x0)
        if first_name and last_name:
            return f"{read_c_string(process, first_name + 0x4, 50)} {read_c_string(process, last_name + 0x4, 50)}"

        full_name = read_uint(process, name_base + 0x48)
        if full_name:
            return read_c_string(process, full_name + 0x4, 255)
    except Exception:
        return None

    return None


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


def _find_manager_address_via_ptr_root(process) -> int:
    if IS_WINDOWS:
        scan_start, scan_end = _get_windows_fm_image_range(process)
    else:
        scan_start, scan_end = process.fm_text_start, process.fm_text_end

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


def open_fm_process():
    if IS_WINDOWS:
        import pymem

        return pymem.Pymem("fm.exe")
    if IS_LINUX:
        return LinuxFmProcess.open()
    raise RuntimeError("Unsupported platform")


def find_manager_address(process=None) -> int:
    process = process or open_fm_process()

    if IS_WINDOWS or IS_LINUX:
        return _find_manager_address_via_ptr_root(process)

    raise RuntimeError("Unsupported platform")


def load_squad_table(target_teams=[22], process=None):
    process = process or open_fm_process()
    target_teams = {target_teams} if isinstance(target_teams, int) else set(target_teams)

    manager_address = find_manager_address(process)
    club_address = follow_pointer_chain(process, manager_address, 0xC8, 0x10, 0x30)
    if not club_address:
        raise RuntimeError("Resolved the manager address, but the club chain returned null")

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
            if not player_address or read_uint(process, player_address) != PLAYER_VTABLE:
                continue

            rows.append(
                [
                    read_player_name(process, player_address + 0x278),
                    read_uint(process, player_address + 0x200, 2),
                    read_uint(process, player_address + 0x202, 2),
                ]
            )

    if not rows:
        return pd.DataFrame(columns=["Name", "CA", "PA"])

    df = pd.DataFrame(rows, columns=["Name", "CA", "PA"])
    return df.sort_values(by=["PA", "CA"], ascending=[False, False]).reset_index(drop=True)
