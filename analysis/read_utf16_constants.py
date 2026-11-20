"""Read UTF-16 string literals the decompiler inlined as SSE comparison constants.

Why this exists: LLVM compiles a C# `switch` over a String into length dispatch plus 16-byte
character compares, so Hex-Rays prints the compared text as `xmmword_145E88A60` instead of a
readable literal. `ida.py` has no byte subcommand and the MCP `get_string` decodes ANSI, not UTF-16,
so this asks the same plugin for raw bytes through the same client and decodes them itself.

The chunk offsets matter. A .NET string object is [MethodTable][length][UTF-16 chars]; chars start at
+12, and the compiler compares overlapping windows (v6+12, v6+20, v6+22, v6+24), so each xmmword is
16 bytes = 8 code units starting at a different character index. That is why the fragments below have
to be read in address order and stitched by their offsets rather than treated as whole strings.
"""
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402  (the same client the rest of the analysis uses)


def read(addr, length=16):
    res = call('get_bytes', {'regions': [{'addr': addr, 'size': length}]})
    if isinstance(res, str):
        import json
        res = json.loads(res)
    blob = res[0]['data']
    out = bytearray()
    for tok in blob.split():
        out.append(int(tok, 16))
    return bytes(out)


def main(argv):
    if not argv:
        print('usage: read_utf16_constants.py <hexaddr> [...]')
        return 2
    for raw in argv:
        addr = raw if raw.startswith('0x') else '0x' + raw
        blob = read(addr, 16)
        units = [int.from_bytes(blob[i:i + 2], 'little') for i in range(0, len(blob) - 1, 2)]
        visible = ''.join(chr(u) if 32 <= u < 127 else ('\u00b7' if u == 0 else '\uff1f') for u in units)
        print('%s  units=%s  text=%s' % (addr, ' '.join('%02x' % u for u in units), visible))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
