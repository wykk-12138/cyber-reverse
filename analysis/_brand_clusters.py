"""R1173: read the neighbourhood of the two brand clusters.

R1172 established that Jacquemus and Maison Margiela are supported stores and that the replica has neither.
The next question is what each store's literal inventory looks like, and the cheapest honest way to ask is
to read the frozen-string neighbourhood around the anchors already found (Jacquemus-Preload at 0x146dd3bb4,
Margiela-Preload at 0x146dfcbec): strings of one type or module tend to be laid out together, so a window
either side shows the region names, controller names and log categories that belong to the same store.
"""
import ida_bytes

WINDOWS = [
    (0x146DD3000, 0x146DD4800, "Jacquemus cluster"),
    (0x146DFB800, 0x146DFD000, "Margiela cluster"),
]


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 120):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        s = body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    return s if s.isprintable() else None


for lo, hi, label in WINDOWS:
    print("=" * 16, label, "%#x..%#x" % (lo, hi))
    found = []
    va = lo
    while va < hi:
        s = frozen(va)
        if s:
            found.append((va, s))
            va += 12 + len(s) * 2
            va = (va + 3) & ~3
        else:
            va += 4
    for va, s in found:
        print("   %#x  %r" % (va, s))
    print("   count:", len(found))
    print()
