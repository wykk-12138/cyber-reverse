"""R1156: every address-citing string constant in the payment layer, compared with the image.

R1155 proved the method on the four documents: parse the replica side from source, take the address from
the constant's own comment, decode the frozen layout, compare character by character. The four documents
were each one newline off while their comments claimed verbatim, so the same question is worth putting to
every other constant that cites an address.

The cited address may be the object header or the character start, and the project has used both
conventions in different places, so each candidate is tried and the one that matches is reported. An
entry that matches at neither is the interesting row.
"""
import io
import re

import ida_bytes

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Payments\PayPalThreeDs.cs"

text = io.open(SRC, encoding="utf-8").read()
lines = text.split("\n")

# public const string Name = "value";  ... // 0xADDR   (single-line, non-verbatim only)
ROW = re.compile(r'public const string (\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;\s*(?://|\uFFFD).*?(0x[0-9A-Fa-f]{6,})')
ADDR_ANY = re.compile(r"(0x[0-9A-Fa-f]{6,})")


def unescape(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            out.append({"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}.get(c, c))
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
    if not (0 < ln < 5000):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


rows = []
DECL = re.compile(r'public const string (\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')
claimed = {}
ambiguous = 0
for idx, line in enumerate(lines):
    m = DECL.search(line)
    if not m:
        continue
    # Same line first, then the contiguous /// block that ends on the line above. Anything looser
    # attributes a neighbour's address to this constant, which is exactly the mistake this comment
    # exists to prevent -- it produced six false DIFFER rows on the first pass.
    addr = None
    hit = ADDR_ANY.search(line)
    if hit:
        addr = int(hit.group(1), 16)
    else:
        back = idx - 1
        block = []
        while back >= 0 and lines[back].strip().startswith("///"):
            block.append(lines[back])
            back -= 1
        for probe in block:                     # nearest doc line first
            hit = ADDR_ANY.search(probe)
            if hit:
                addr = int(hit.group(1), 16)
                break
    if addr is None:
        continue
    if addr in claimed:
        ambiguous += 1                          # two constants citing one address: refuse to judge
        continue
    claimed[addr] = m.group(1)
    rows.append((m.group(1), unescape(m.group(2)), addr, idx + 1))

print("constants citing an address:", len(rows))
exact, objhdr, differ, unread = [], [], [], []
for name, value, addr, line_no in rows:
    if frozen(addr) == value:
        exact.append((name, addr, line_no))
        continue
    if frozen(addr - 12) == value:
        objhdr.append((name, addr, line_no))
        continue
    got = frozen(addr) or frozen(addr - 12)
    if got is None:
        unread.append((name, addr, line_no))
        continue
    differ.append((name, addr, line_no, value, got))

print()
print("IDENTICAL at the cited address      :", len(exact))
print("IDENTICAL at cited-12 (obj header)  :", len(objhdr))
print("DIFFER                              :", len(differ))
print("UNREADABLE                          :", len(unread))

for name, addr, line_no, value, got in differ:
    n = min(len(value), len(got))
    k = next((i for i in range(n) if value[i] != got[i]), n)
    print()
    print("  %-28s line %-5d %#x" % (name, line_no, addr))
    print("     replica (%d): %r" % (len(value), value[:120]))
    print("     image   (%d): %r" % (len(got), got[:120]))
    print("     first diff at %d" % k)

for name, addr, line_no in unread:
    print("  UNREADABLE %-28s line %-5d %#x" % (name, line_no, addr))
