"""R699: make every exported function inventory state whether symbols were loaded.

BLOCKERS §45 (R612): "同口径" pinned the analysis options but not the symbol input. R613 measured the effect --
`cc` 129 with no PDB vs 1 with it, and 186,732 vs 187,698 functions. Without a record in the data itself, a difference
of that size reads as "the artifact changed".

**Criterion, fixed before writing**: line 1 of every exported file starts with `# exportspec symbols=` and the value is
`yes` / `no` / `unknown`. Tab-free, so `load_rows` (which requires three tab-separated fields) skips it.

**How symbols are detected**: no `server_health` field reports it. The proxy is the share of functions whose name is
not `sub_*`: R613's own baselines are 175,104/187,698 = 93% with symbols and 3,936/186,732 = 2.1% without, an order of
magnitude apart. So >0.5 -> yes, <0.1 -> no, otherwise unknown. **This is Inference from a measured baseline, not an
Observation of a flag** -- and the header prints the raw ratio so a reader can disagree.
"""

import io
import subprocess

PATH = r"D:\projects\cyber-reverse\analysis\func_compare.py"

OLD_TEMPLATE = '''EXPORT_TEMPLATE = "\\n".join([
    "import idautils, ida_funcs",
    "rows = []",
    "for ea in idautils.Functions():",
    "    f = ida_funcs.get_func(ea)",
    "    rows.append((ea, f.size() if f else 0, ida_funcs.get_func_name(ea) or ''))",
    "lines = ['%x\\\\t%d\\\\t%s' % r for r in rows]",
    "open(__DEST__, 'w', encoding='utf-8', newline=chr(10)).write(chr(10).join(lines))",
    "print('EXPORTED', len(rows))",
])'''

NEW_TEMPLATE = '''EXPORT_TEMPLATE = "\\n".join([
    "import idautils, ida_funcs",
    "rows = []",
    "for ea in idautils.Functions():",
    "    f = ida_funcs.get_func(ea)",
    "    rows.append((ea, f.size() if f else 0, ida_funcs.get_func_name(ea) or ''))",
    # R699: record whether symbols were loaded, in the data itself (BLOCKERS 45 / R613: cc 129 vs 1,
    # 186,732 vs 187,698 functions -- without this, such a gap reads as 'the artifact changed').
    # Proxy: share of non-sub_ names. R613 baselines are 93% with symbols and 2.1% without.
    "named = sum(1 for _e, _s, n in rows if n and not n.startswith('sub_'))",
    "ratio = (float(named) / len(rows)) if rows else 0.0",
    "symbols = 'yes' if ratio > 0.5 else ('no' if ratio < 0.1 else 'unknown')",
    "hdr = '# exportspec symbols=%s named=%d total=%d ratio=%.4f' % (symbols, named, len(rows), ratio)",
    "lines = [hdr] + ['%x\\\\t%d\\\\t%s' % r for r in rows]",
    "open(__DEST__, 'w', encoding='utf-8', newline=chr(10)).write(chr(10).join(lines))",
    "print('EXPORTED', len(rows))",
    "print('EXPORTSPEC', hdr)",
])'''


def main():
    text = io.open(PATH, encoding="utf-8").read()
    if "R699" in text:
        print("already patched")
        return
    if OLD_TEMPLATE not in text:
        print("MISS template anchor")
        # show the actual block so the mismatch is evidence-based
        i = text.find("EXPORT_TEMPLATE")
        print(repr(text[i:i + 620]))
        return
    text = text.replace(OLD_TEMPLATE, NEW_TEMPLATE, 1)

    # surface the spec after export, and verify the file really carries it
    old_tail = '''    if not os.path.exists(dest):
        raise SystemExit("%s: IDA reported %s rows but %s is absent" % (label, m.group(1), dest))
    return int(m.group(1)), health'''
    new_tail = '''    if not os.path.exists(dest):
        raise SystemExit("%s: IDA reported %s rows but %s is absent" % (label, m.group(1), dest))

    # R699: the file must say whether symbols were loaded -- read it back rather than trusting stdout.
    with io.open(dest, encoding="utf-8", errors="replace") as fh:
        first = fh.readline().rstrip("\\n")
    if not first.startswith("# exportspec symbols="):
        raise SystemExit("%s: %s has no exportspec header (first line: %r)" % (label, dest, first[:120]))
    print("  %s: %s" % (label, first))
    return int(m.group(1)), health'''
    if old_tail in text:
        text = text.replace(old_tail, new_tail, 1)
        print("patched: export() now verifies and prints the header")
    else:
        print("WARN: tail anchor not found -- template only")

    import ast
    ast.parse(text)
    io.open(PATH, "w", encoding="utf-8").write(text)
    print("written")


if __name__ == "__main__":
    main()
