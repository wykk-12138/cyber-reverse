"""Shared read-only PE access that does not pull the whole 129 MB image into RAM. (R684)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session, and the public tools in
`seep-reverse-lab` / `rea` do not ship a "read a byte range at an RVA" utility -- `pe_strings.py` is the in-repo
extractor and it works on the whole file at once.

**Why now**: the session ran out of memory and the machine was restarted. The heavy commands are not individually
large, but several analysis scripts each do `open(EXE, "rb").read()` -- 129,243,216 bytes per call -- and one of them
(`pe_strings_utf8.py`) additionally builds 193,556 strings. Repeating that across a long session accumulates. This
module replaces the full read with an `mmap`, so the pages are only faulted in as they are touched, and adds a free
memory check so a script refuses to start when the box is already tight.

Nothing here changes any conclusion: every number in the earlier rounds came from the same bytes.

Usage:

    from pe_reader import Pe
    with Pe(r"D:\\projects\\cyber-reverse\\target\\Cybersole.exe") as pe:
        pe.check_memory()
        data = pe.at(0x037D4BC4, 64)      # bytes at an RVA
        off  = pe.off(0x037D4BC4)          # RVA -> file offset
        for m in pe.find(b"country\\x00"):  # mmap scan, no copy
            ...
"""

import mmap
import struct

# refuse to start below this; the project rule is 2 GB for builds, 1 GB to stop entirely
MIN_FREE_GB = 1.5


def free_gb():
    """Free physical memory in GB, or None when it cannot be read."""
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return None
        return stat.ullAvailPhys / (1024.0 ** 3)
    except Exception:
        return None


class Pe:
    """Read-only view over a PE file backed by mmap."""

    def __init__(self, path):
        self.path = path
        self._fh = open(path, "rb")
        self.file_size = self._fh.seek(0, 2)
        self._fh.seek(0)
        self.data = mmap.mmap(self._fh.fileno(), 0, access=mmap.ACCESS_READ)
        self.sections = self._sections()

    # -- lifecycle -------------------------------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def close(self):
        try:
            self.data.close()
        finally:
            self._fh.close()

    # -- headers ---------------------------------------------------------------------------------------------
    def _sections(self):
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        nsec = struct.unpack_from("<H", self.data, pe + 6)[0]
        opt = struct.unpack_from("<H", self.data, pe + 20)[0]
        base = pe + 24 + opt
        out = []
        for i in range(nsec):
            off = base + i * 40
            name = self.data[off:off + 8].rstrip(b"\x00").decode("ascii", "replace")
            vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", self.data, off + 8)
            out.append((name, vaddr, max(vsize, rsize), roff))
        return out

    # -- addressing ------------------------------------------------------------------------------------------
    def off(self, rva):
        """RVA -> file offset, or None when unmapped."""
        for _name, vaddr, size, roff in self.sections:
            if vaddr <= rva < vaddr + size:
                return roff + (rva - vaddr)
        return None

    def rva(self, off):
        """File offset -> RVA, or None."""
        for _name, vaddr, size, roff in self.sections:
            if roff <= off < roff + size:
                return vaddr + (off - roff)
        return None

    def at(self, rva, n):
        """n bytes at an RVA (a copy; use `slice` for a view)."""
        o = self.off(rva)
        return None if o is None else self.data[o:o + n]

    def slice(self, rva_off, n):
        """Memoryview of n bytes at a FILE OFFSET -- no copy."""
        return memoryview(self.data)[rva_off:rva_off + n]

    def find(self, needle, start_off=0, end_off=None):
        """Yield file offsets of `needle`, scanning the mmap in place."""
        end = len(self.data) if end_off is None else end_off
        pos = start_off
        while True:
            hit = self.data.find(needle, pos, end)
            if hit < 0:
                return
            yield hit
            pos = hit + 1

    def u32(self, file_off):
        return struct.unpack_from("<I", self.data, file_off)[0]

    # -- safety ----------------------------------------------------------------------------------------------
    def check_memory(self, minimum=None):
        """Raise when free physical memory is below the floor, so a script does not add to the pressure."""
        need = MIN_FREE_GB if minimum is None else minimum
        gb = free_gb()
        if gb is None:
            print("  [memory] unreadable; continuing")
            return
        print("  [memory] free %.2f GB (floor %.2f GB)" % (gb, need))
        if gb < need:
            raise SystemExit("free memory %.2f GB is below the %.2f GB floor -- free memory first" % (gb, need))
