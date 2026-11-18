"""R1155: are the four graphql documents byte-for-byte the image's?

R1154 left this open: the class carries four verbatim strings and its comments cite an object address
and a character count for each, but nothing had ever compared the text. This reads both sides and
reports the first place they differ, if any.

The replica side is parsed from the source itself (the constants are `@"..."` verbatim strings), and the
address for each is taken from the doc comment immediately above it, so no address is transcribed by
hand. The image side is the NativeAOT frozen layout: [MethodTable*:8][Length:4][UTF-16 chars].
"""
import io
import re

import ida_bytes

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Payments\PayPalThreeDs.cs"

text = io.open(SRC, encoding="utf-8").read()
lines = text.split("\n")

# name -> (address, chars) from the comment, and the verbatim body
decl = re.compile(r"public const string (\w+Document)\s*=\s*@\"", re.M)
ADDR = re.compile(r"obj\s+(0x[0-9A-Fa-f]+)")

rows = []
for m in decl.finditer(text):
    name = m.group(1)
    # the doc comment is the nearest preceding line carrying "obj 0x..."
    head = text[: m.start()].rstrip().split("\n")[-1]
    a = ADDR.search(head)
    if not a:
        print("!! no address on the comment above", name)
        continue
    addr = int(a.group(1), 16)

    # walk the verbatim string: from just after @" to the closing " that is not doubled
    i = m.end()
    out = []
    while i < len(text):
        ch = text[i]
        if ch == '"':
            if i + 1 < len(text) and text[i + 1] == '"':
                out.append('"')
                i += 2
                continue
            break
        out.append(ch)
        i += 1
    rows.append((name, addr, "".join(out)))


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    return body.decode("utf-16-le", "replace")


for name, addr, replica in rows:
    image = frozen(addr)
    if image is None:
        print("%-22s %#x  IMAGE UNREADABLE" % (name, addr))
        continue
    if image == replica:
        print("%-22s %#x  IDENTICAL  (%d chars)" % (name, addr, len(replica)))
        continue
    n = min(len(image), len(replica))
    k = next((i for i in range(n) if image[i] != replica[i]), n)
    print("%-22s %#x  DIFFER  image=%d replica=%d  first diff at %d"
          % (name, addr, len(image), len(replica), k))
    lo = max(0, k - 40)
    print("    image  ...%r" % image[lo:k + 40])
    print("    replica...%r" % replica[lo:k + 40])
