# Resolve every off_/unk_ data reference in the LicenseControl main decompilation.
# Runs on raw file bytes; no IDA session needed. Output: analysis/license_refs_resolved.txt
import io
import re
import struct

data = io.open(r"D:\projects\cyber-reverse\target\Cybersole.exe", "rb").read()


def read(va, n):
    if 0x146A47000 <= va < 0x146A47000 + 0x9C1000:
        fo = 0x6A45C00 + (va - 0x146A47000)
    elif 0x14314E000 <= va < 0x14314E000 + 0x38F8A00:
        fo = 0x314D200 + (va - 0x14314E000)
    else:
        return None
    return data[fo:fo + n]


def as_str(b):
    """Return the string if b looks like [mt:8][len:4][utf16], else None."""
    if b is None or len(b) < 12:
        return None
    ln = struct.unpack_from("<i", b, 8)[0]
    if not (0 < ln <= 128):
        return None
    if len(b) < 12 + ln * 2:
        return None
    ch = b[12:12 + ln * 2].decode("utf-16-le", "replace")
    if ch.isprintable() and "\x00" not in ch:
        return (ln, ch)
    return None


code = io.open(r"D:\projects\cyber-reverse\analysis\license_control_main.c", encoding="utf-8").read()
names = sorted(set(int(x, 16) for x in re.findall(r"(?:off|unk)_([0-9A-F]+)", code)))

out = []
for va in names:
    b = read(va, 12 + 300)
    if b is None:
        out.append("0x%X  <unmapped>" % va)
        continue
    s = as_str(b)
    if s:
        out.append("0x%X  STR  len=%d %r" % (va, s[0], s[1]))
        continue
    # try: pointer table -- resolve first 4 qwords as string objects
    qs = struct.unpack_from("<QQQQ", b, 0)
    tags = []
    for q in qs:
        if q:
            s2 = as_str(read(q, 12 + 200))
            tags.append(repr(s2[1]) if s2 else "0x%X" % q)
        else:
            tags.append("0")
    out.append("0x%X  PTRS %s" % (va, " ".join(tags)))

io.open(r"D:\projects\cyber-reverse\analysis\license_refs_resolved.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
print("total refs:", len(out))
