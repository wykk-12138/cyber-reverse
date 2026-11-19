"""R1173: measure store coverage against the image's alphabetical name pool.

R1172 found two missing stores by accident. The cluster dump shows why they were easy to miss and easy to
find: the image keeps store names, region names and controller names in one huge alphabetically sorted
frozen-string pool, so a store can be located by name but nothing announces the list's extent. This walks
a wide window, keeps the longest run that stays in non-decreasing order, and prints that run - which is the
pool - so the replica's own list can be diffed against a measurement instead of against a memory.
"""
import ida_bytes

LO, HI = 0x146D00000, 0x146E00000


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 90):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        s = body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    return s if s.isprintable() and s.strip() == s and s else None


items = []
va = LO
while va < HI:
    s = frozen(va)
    if s:
        items.append((va, s))
        va += 12 + len(s) * 2
        va = (va + 3) & ~3
    else:
        va += 4

print("strings in window:", len(items))

# longest non-decreasing run by case-insensitive comparison
best, cur = [], []
for i, (va, s) in enumerate(items):
    if cur and s.lower() < cur[-1][1].lower():
        if len(cur) > len(best):
            best = cur
        cur = []
    cur.append((va, s))
if len(cur) > len(best):
    best = cur

print("longest sorted run:", len(best), "items")
if best:
    print("  from %#x %r  to %#x %r" % (best[0][0], best[0][1], best[-1][0], best[-1][1]))
    with open(r"D:\projects\cyber-reverse\analysis\.image_name_pool.txt", "w", encoding="utf-8") as fh:
        for va, s in best:
            fh.write("%#x\t%s\n" % (va, s))
    print("  wrote analysis/.image_name_pool.txt")
