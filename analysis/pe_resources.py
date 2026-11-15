r"""Walk both PE resource trees and compare them leaf by leaf.

WHY THIS TOOL EXISTS (AGENTS.md §1.2 requires the reason be stated):
Claim C5 says `资源面相同 = fail, pe_triage.py (12 <-> 2)` and stops there. `pe_triage.py` counts leaves; it
does not say **what** the twelve are, so the claim has never been more than a number. Accepting a difference
without naming it is exactly what R442 showed to be dangerous (the "MonitorConcurrency is invented" line
survived 50 rounds because nobody wrote it as a checkable condition).

This parses the IMAGE_RESOURCE_DIRECTORY tree directly (type -> name -> language) for both images and prints
every leaf with its size, then the set difference. No third-party library: the structure is small and the
point is to be able to say "leaf X of N bytes exists on one side only".

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/pe_resources.py
    python analysis/pe_resources.py --side original
Output: analysis/pe_resources.md
"""

import argparse
import io
import os
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL = os.path.join(ROOT, "target", "Cybersole.exe")
REPLICA = os.path.join(ROOT, "replica", ".publish-aot", "Cybersole.Ui.exe")
OUT = os.path.join(ROOT, "analysis", "pe_resources.md")

RT_NAMES = {
    1: "CURSOR", 2: "BITMAP", 3: "ICON", 4: "MENU", 5: "DIALOG", 6: "STRING", 7: "FONTDIR", 8: "FONT",
    9: "ACCELERATOR", 10: "RCDATA", 11: "MESSAGETABLE", 12: "GROUP_CURSOR", 14: "GROUP_ICON",
    16: "VERSION", 17: "DLGINCLUDE", 19: "PLUGPLAY", 20: "VXD", 21: "ANICURSOR", 22: "ANIICON",
    23: "HTML", 24: "MANIFEST",
}


def rva_to_offset(sections, rva):
    for va, vsize, raw_ptr, raw_size in sections:
        if va <= rva < va + max(vsize, raw_size):
            return raw_ptr + (rva - va)
    return None


def read_sections(data):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise SystemExit("not a PE file")
    coff = e_lfanew + 4
    num_sections = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    dd = opt + (112 if magic == 0x20B else 96)
    res_rva, res_size = struct.unpack_from("<II", data, dd + 2 * 8)
    sect = opt + opt_size
    sections = []
    for i in range(num_sections):
        base = sect + i * 40
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((va, vsize, raw_ptr, raw_size))
    return sections, res_rva, res_size


def walk(data, sections, base_off, dir_off, path, leaves):
    n_named, n_id = struct.unpack_from("<HH", data, dir_off + 12)
    count = n_named + n_id
    for i in range(count):
        entry = dir_off + 16 + i * 8
        name_field, data_field = struct.unpack_from("<II", data, entry)
        if name_field & 0x80000000:
            str_off = base_off + (name_field & 0x7FFFFFFF)
            length = struct.unpack_from("<H", data, str_off)[0]
            label = data[str_off + 2:str_off + 2 + length * 2].decode("utf-16-le", "replace")
        else:
            ident = name_field & 0xFFFF
            label = RT_NAMES.get(ident, str(ident)) if len(path) == 0 else str(ident)
        if data_field & 0x80000000:
            walk(data, sections, base_off, base_off + (data_field & 0x7FFFFFFF), path + [label], leaves)
        else:
            leaf = base_off + data_field
            rva, size = struct.unpack_from("<II", data, leaf)
            offset = rva_to_offset(sections, rva)
            leaves.append(("/".join(path + [label]), size, rva, offset))


def resources(path):
    data = io.open(path, "rb").read()
    sections, res_rva, res_size = read_sections(data)
    if not res_rva:
        return [], len(data)
    base_off = rva_to_offset(sections, res_rva)
    leaves = []
    walk(data, sections, base_off, base_off, [], leaves)
    return leaves, len(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--side", choices=["both", "original", "replica"], default="both")
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)

    sides = []
    if args.side in ("both", "original"):
        sides.append(("原版", ORIGINAL))
    if args.side in ("both", "replica"):
        sides.append(("复刻件", REPLICA))

    results = {}
    for label, path in sides:
        if not os.path.exists(path):
            print("%s: MISSING %s" % (label, path))
            continue
        leaves, size = resources(path)
        results[label] = (leaves, size)
        print("%s: %d leaves (%d bytes)" % (label, len(leaves), size))

    lines = ["# PE 资源树对照（生成文件，请勿手改）", "",
             "> 由 `python analysis/pe_resources.py` 生成：直接解析 IMAGE_RESOURCE_DIRECTORY 三层树",
             "> （type → name → language），逐叶子列出。claim C5 此前只有一个数（12 ↔ 2），没有内容。", ""]

    for label, (leaves, size) in results.items():
        lines += ["## %s（%d 个叶子）" % (label, len(leaves)), "",
                  "| 路径 | 字节 | RVA |", "|---|---|---|"]
        for name, leaf_size, rva, _off in sorted(leaves):
            lines.append("| `%s` | %d | 0x%X |" % (name, leaf_size, rva))
        lines.append("")

    if len(results) == 2:
        o = {n for n, *_ in results["原版"][0]}
        r = {n for n, *_ in results["复刻件"][0]}
        lines += ["## 差集", "",
                  "### 原版有、复刻件没有：%d" % len(o - r), ""]
        for name in sorted(o - r):
            size = next(s for n, s, *_ in results["原版"][0] if n == name)
            lines.append("- `%s`（%d 字节）" % (name, size))
        lines += ["", "### 复刻件有、原版没有：%d" % len(r - o), ""]
        for name in sorted(r - o):
            size = next(s for n, s, *_ in results["复刻件"][0] if n == name)
            lines.append("- `%s`（%d 字节）" % (name, size))
        lines.append("")

    io.open(args.out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print()
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
