"""Cross-platform process memory helpers for Football Manager."""

import ctypes
import ctypes.util
from pathlib import Path

from core.platform import IS_WINDOWS

FM_EXE_PATH_FRAGMENT = "/Football Manager 2024/fm.exe"


class IOVec(ctypes.Structure):
    _fields_ = [("iov_base", ctypes.c_void_p), ("iov_len", ctypes.c_size_t)]


class LinuxFmProcess:
    def __init__(self, pid):
        self.pid = pid
        libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        self._readv = libc.process_vm_readv
        self._readv.argtypes = [ctypes.c_int, ctypes.POINTER(IOVec), ctypes.c_ulong, ctypes.POINTER(IOVec), ctypes.c_ulong, ctypes.c_ulong]
        self._readv.restype = ctypes.c_ssize_t
        self.fm_text_start, self.fm_text_end = self._find_text_range()

    @classmethod
    def open(cls):
        return cls(_find_linux_fm_pid())

    def _find_text_range(self):
        regions = list(self.iter_memory_regions())
        marker_index = next(
            (index for index, (_, _, _, path) in enumerate(regions) if FM_EXE_PATH_FRAGMENT in path or path.endswith("/fm.exe")), None
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

    def iter_memory_regions(self):
        with Path(f"/proc/{self.pid}/maps").open() as fh:
            for line in fh:
                parts = line.split(maxsplit=5)
                start_s, end_s = parts[0].split("-")
                perms = parts[1]
                path = parts[5].strip() if len(parts) > 5 else ""
                yield int(start_s, 16), int(end_s, 16), perms, path

    def read_bytes(self, address, size):
        buffer = ctypes.create_string_buffer(size)
        local = IOVec(ctypes.cast(buffer, ctypes.c_void_p), size)
        remote = IOVec(ctypes.c_void_p(address), size)
        bytes_read = self._readv(self.pid, ctypes.byref(local), 1, ctypes.byref(remote), 1, 0)
        if bytes_read != size:
            err = ctypes.get_errno()
            raise OSError(err, f"process_vm_readv returned {bytes_read} bytes, expected {size}")
        return bytes(buffer.raw)


def _find_linux_fm_pid():
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


def open_fm_process():
    if IS_WINDOWS:
        import pymem

        return pymem.Pymem("fm.exe")
    return LinuxFmProcess.open()


def get_fm_base_address(process):
    if IS_WINDOWS:
        import pymem.process

        module = pymem.process.module_from_name(process.process_handle, "fm.exe")
        if module is None:
            raise RuntimeError("Could not find fm.exe in the target process module list")
        return int(module.lpBaseOfDll)

    for start, _end, _perms, path in process.iter_memory_regions():
        if FM_EXE_PATH_FRAGMENT in path or path.endswith("/fm.exe"):
            return start

    raise RuntimeError("Could not find a base mapping for fm.exe")


def get_fm_image_range(process):
    if IS_WINDOWS:
        import pymem.process

        module = pymem.process.module_from_name(process.process_handle, "fm.exe")
        if module is None:
            raise RuntimeError("Could not find fm.exe in the target process module list")

        base_address = int(module.lpBaseOfDll)
        image_size = int(module.SizeOfImage)
        return base_address, base_address + image_size

    return process.fm_text_start, process.fm_text_end


def read_uint(process, address, size=8):
    return int.from_bytes(process.read_bytes(address, size), byteorder="little")


def read_c_string(process, address, size):
    raw = process.read_bytes(address, size).split(b"\x00", 1)[0]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def read_pointer(process, address):
    pointer = read_uint(process, address)
    return pointer or None


def read_chained_value(process, base_address, pointer_offsets, final_offset, *, size):
    current = base_address
    for offset in pointer_offsets:
        current = read_pointer(process, current + offset)
        if current is None:
            return None
    return read_uint(process, current + final_offset, size)


def read_chained_string(process, base_address, pointer_offsets, final_offset, *, size):
    current = base_address
    for offset in pointer_offsets:
        current = read_pointer(process, current + offset)
        if current is None:
            return None
    return read_c_string(process, current + final_offset, size)


def follow_pointer_chain(process, base_address, *offsets):
    current = base_address
    for offset in offsets:
        current = read_uint(process, current + offset)
        if current == 0:
            return None
    return current


def iter_pattern_matches(
    process, pattern, *, writable=None, executable=None, private=None, chunk_size=0x200000
):
    if IS_WINDOWS:
        for address in process.pattern_scan_all(pattern, return_multiple=True):
            yield int(address)
        return

    overlap = len(pattern) - 1
    for start, end, perms, _path in process.iter_memory_regions():
        if "r" not in perms:
            continue
        if writable is not None and ("w" in perms) != writable:
            continue
        if executable is not None and ("x" in perms) != executable:
            continue
        if private is not None and (perms[3] == "p") != private:
            continue

        carry = b""
        address = start
        while address < end:
            size = min(chunk_size, end - address)
            try:
                data = carry + process.read_bytes(address, size)
            except OSError:
                break

            base = address - len(carry)
            search_from = 0
            while True:
                index = data.find(pattern, search_from)
                if index == -1:
                    break
                yield base + index
                search_from = index + 1

            carry = data[-overlap:] if overlap > 0 else b""
            address += size
