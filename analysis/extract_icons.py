r"""Extract the original's icon set and rebuild it as a single .ico for the replica.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
`pe_resources.py` (R447) showed the replica ships **no icon at all** — the original carries nine `RT_ICON`
leaves plus a `RT_GROUP_ICON`, and the replica has only MANIFEST + VERSION. Claim C5 had been sitting as
"资源面不同, fail" with no content; the actual defect is "the app has no icon", and it is fixable rather
than something to accept.

`pe_triage.py` reports resource *counts* and nothing more, so it cannot help here. This reads the group icon
(the authoritative list of sizes/ids), pulls each `RT_ICON` blob out of the original, and writes a proper
ICO container: ICONDIR + one ICONDIRENTRY per image + the raw image bytes. Windows accepts PNG-compressed
entries (Vista+) as well as DIB entries, so the blobs are copied verbatim — no re-encoding, nothing invented.

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis\extract_icons.py --out replica\assets\cybersole.ico
"""

import argparse
import io
import os
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.join(ROOT, "target", "Cybersole.exe")


def read_sections(data):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    coff = e_lfanew + 4
    num_sections = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    dd = opt + (112 if magic == 0x20B else 96)
    res_rva, _res_size = struct.unpack_from("<II", data, dd + 2 * 8)
    sect = opt + opt_size
    sections = []
    for i in range(num_sections):
        base = sect + i * 40
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((va, vsize, raw_ptr, raw_size))
    return sections, res_rva


def rva_to_offset(sections, rva):
    for va, vsize, raw_ptr, raw_size in sections:
        if va <= rva < va + max(vsize, raw_size):
            return raw_ptr + (rva - va)
    return None


def leaves(data, sections, base_off, dir_off, path, out):
    n_named, n_id = struct.unpack_from("<HH", data, dir_off + 12)
    for i in range(n_named + n_id):
        entry = dir_off + 16 + i * 8
        name_field, data_field = struct.unpack_from("<II", data, entry)
        if name_field & 0x80000000:
            str_off = base_off + (name_field & 0x7FFFFFFF)
            length = struct.unpack_from("<H", data, str_off)[0]
            label = data[str_off + 2:str_off + 2 + length * 2].decode("utf-16-le", "replace")
        else:
            label = str(name_field & 0xFFFF)
        if data_field & 0x80000000:
            leaves(data, sections, base_off, base_off + (data_field & 0x7FFFFFFF), path + [label], out)
        else:
            leaf = base_off + data_field
            rva, size = struct.unpack_from("<II", data, leaf)
            off = rva_to_offset(sections, rva)
            # path is [type, name, language]; RT_GROUP_ICON references the *name* level. Using `label` here
            # gave the language ("0") for every icon, so every group entry looked up a missing id.
            out.setdefault(path[0], []).append((path[1], rva, size, off))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--exe", default=ORIGINAL)
    parser.add_argument("--out", default=os.path.join(ROOT, "replica", "assets", "cybersole.ico"))
    args = parser.parse_args(argv)

    data = io.open(args.exe, "rb").read()
    sections, res_rva = read_sections(data)
    base_off = rva_to_offset(sections, res_rva)
    found = {}
    leaves(data, sections, base_off, base_off, [], found)

    icons = {int(name): (rva, size, off) for name, rva, size, off in found.get("3", [])}
    groups = found.get("14", [])
    if not icons or not groups:
        raise SystemExit("no icon resources found")

    _gname, grva, gsize, goff = groups[0]
    group = data[goff:goff + gsize]
    reserved, kind, count = struct.unpack_from("<HHH", group, 0)
    if reserved != 0 or kind != 1:
        raise SystemExit("unexpected group icon header")

    entries = []
    for i in range(count):
        base = 6 + i * 14
        width, height, colors, res, planes, bits, bytes_in_res, ident = struct.unpack_from("<BBBBHHIH", group, base)
        if ident not in icons:
            raise SystemExit("group references icon id %d that is absent" % ident)
        _rva, size, off = icons[ident]
        entries.append((width, height, colors, res, planes, bits, size, data[off:off + size]))

    # ICO: 6-byte header, 16-byte entry per image, then the images back to back.
    header = struct.pack("<HHH", 0, 1, len(entries))
    offset = 6 + 16 * len(entries)
    table = b""
    blobs = b""
    for width, height, colors, res, planes, bits, size, blob in entries:
        table += struct.pack("<BBBBHHII", width, height, colors, res, planes, bits, size, offset)
        blobs += blob
        offset += size

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    io.open(args.out, "wb").write(header + table + blobs)

    print("wrote %s" % args.out)
    print("  images: %d" % len(entries))
    for width, height, _c, _r, _p, bits, size, blob in entries:
        kind_label = "PNG" if blob[:8] == b"\x89PNG\r\n\x1a\n" else "DIB"
        print("    %3dx%-3d %2d-bit %7d bytes %s" % (width or 256, height or 256, bits, size, kind_label))
    print("  total: %d bytes" % (len(header) + len(table) + len(blobs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
