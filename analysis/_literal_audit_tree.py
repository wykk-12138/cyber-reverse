"""R1157: the same comparison, on every source file that cites an address beside a string constant.

R1156 ran it over PayPalThreeDs.cs and found a clean sheet. This repeats it over the whole Stores tree so
the claim is not limited to one file. The attribution rule is the one R1156 had to arrive at the hard
way: an address counts only on the declaration line or in the contiguous /// block directly above, and
an address claimed by two constants is refused rather than guessed.
"""
import glob
import io
import os
import re

import ida_bytes

ROOT = r"D:\projects\cyber-reverse\replica\src"

DECL = re.compile(r'(?:public|private|internal|protected) const string (\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')
ADDR_ANY = re.compile(r"(0x1[0-9A-Fa-f]{7,})")


def unescape(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append({"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}.get(s[i + 1], s[i + 1]))
            i += 2
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 20000):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


files = sorted(glob.glob(os.path.join(ROOT, "**", "*.cs"), recursive=True))
print("source files:", len(files))

exact, differ, unread, suffix = [], [], [], []

for path in files:
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        m = DECL.search(line)
        if not m:
            continue
        hit = ADDR_ANY.search(line)
        addr = int(hit.group(1), 16) if hit else None
        if addr is None:
            back, block = idx - 1, []
            while back >= 0 and lines[back].strip().startswith("///"):
                block.append(lines[back])
                back -= 1
            for probe in block:
                hit = ADDR_ANY.search(probe)
                if hit:
                    addr = int(hit.group(1), 16)
                    break
        if addr is None:
            continue

        value = unescape(m.group(2))
        got = frozen(addr)
        if got is None:
            got = frozen(addr - 12)
        if got is None:
            unread.append((os.path.basename(path), m.group(1), idx + 1, addr))
            continue
        row = (os.path.basename(path), m.group(1), idx + 1, addr, value, got)
        if got == value:
            exact.append(row)
        elif value and got.endswith(value):
            # The replica may keep a path and compose the host from a sibling constant, which is a
            # split of the same literal rather than a difference. The prefix has to be accounted for
            # by a constant in the same file, otherwise it is still a difference.
            prefix = got[: -len(value)]
            prefix_known = any(
                DECL.search(other) and unescape(DECL.search(other).group(2)) == prefix
                for other in lines
            )
            (suffix if prefix_known else differ).append(
                row + (prefix, prefix_known))
        else:
            differ.append(row + ("", False))

print()
print("IDENTICAL :", len(exact))
print("SUFFIX    :", len(suffix), "(a path constant whose host prefix is a constant in the same file)")
print("DIFFER    :", len(differ))
print("UNREADABLE:", len(unread))
print()
for row in differ:
    name_file, name, line_no, addr, value, got = row[:6]
    n = min(len(value), len(got))
    k = next((i for i in range(n) if value[i] != got[i]), n)
    print("  DIFFER %s:%d %s @%#x" % (name_file, line_no, name, addr))
    print("     replica(%d): %r" % (len(value), value[:100]))
    print("     image  (%d): %r" % (len(got), got[:100]))
    print("     first diff at %d" % k)
for name_file, name, line_no, addr in unread[:12]:
    print("  UNREADABLE %s:%d %s @%#x" % (name_file, line_no, name, addr))
