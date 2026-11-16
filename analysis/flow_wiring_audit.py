"""Which registry entries use a class that is not their own? (R771)

offspring turned out to be registered as `HybrisFlow("offspring", ...)` while an `OffspringFlow` exists with the
identical identity and is never constructed anywhere -- and the image's actual surface is neither, it is a Poq platform
host. One instance of a mismatch raises the question of how many others there are.

This compares two things per module: the flow type the registry actually constructs, and whether a class whose name
matches the module id exists. A module whose own class exists but is unused is either an oversight in the registry or a
deliberate choice that should be written down; either way it is worth naming.

**Why not an existing tool** (AGENTS.md §1.2): this reads this repo's own declarations on both sides. `store_catalog.py`
already resolves the flow type per entry, so the new part is the reverse index -- declared flow classes that no entry
constructs -- plus the name match.
"""

import io
import os
import re
import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import store_catalog as sc  # noqa: E402


def declared_flows():
    """Every concrete StoreFlow subclass declared under src, with the file it lives in."""
    out = {}
    for path in sc.csharp_files():
        text = io.open(path, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"class\s+(\w*(?:Flow|Module))\s*:\s*([\w<>]+)", text):
            out[m.group(1)] = (m.group(2), os.path.basename(path))
    return out


def main():
    declared = declared_flows()
    body = sc.create_all_body(io.open(sc.REGISTRY, encoding="utf-8", errors="replace").read())
    if body is None:
        print("  CreateAll() not found")
        return 1

    used, rows = set(), []
    for m in sc.ENTRY.finditer(body):
        typ = m.group(1) or m.group(3)
        args = m.group(2) or ""
        used.add(typ)
        strs = re.findall(r'"([^"]*)"', args)
        inline_id = strs[0] if len(strs) >= 2 and "new[]" in args else None
        if inline_id is None:
            b = sc.class_body(typ)
            inline_id = sc.prop(b, "Id") if b else None
        rows.append((typ, inline_id))

    print("  flow classes declared under src : %d" % len(declared))
    print("  distinct types the registry uses: %d" % len(used))
    print()

    # a declared *Flow class that nothing constructs
    dead = sorted(t for t in declared if t.endswith("Flow") and t not in used)
    print("  declared Flow classes never constructed (%d):" % len(dead))
    for t in dead:
        base, where = declared[t]
        print("    %-24s : %-16s  %s" % (t, base, where))

    print()
    # A never-constructed class is only suspicious if it is a leaf. MagentoFlow is never constructed directly
    # because every Magento store extends it, which is normal. A leaf that nothing constructs and that shares a
    # module's id is either an oversight in the registry or a decision that was never written down.
    #
    # R771: the first version of this check compared `typ` against `typ + "Flow"`, which can never match because
    # typ already ends in Flow -- so it reported zero mismatches no matter what. Running it and reading the output
    # is what exposed that; the number was never evidence.
    bases = {base for _t, (base, _f) in declared.items()}
    leaves = [t for t in declared if t.endswith("Flow") and t not in used and t not in bases]
    ids = {i for _t, i in rows if i}

    print("  never constructed (%d):" % len([t for t in declared if t.endswith("Flow") and t not in used]))
    for t in sorted(t for t in declared if t.endswith("Flow") and t not in used):
        base, where = declared[t]
        kind = "base class, normal" if t in bases else "LEAF"
        print("    %-22s : %-16s  %-18s %s" % (t, base, kind, where))

    print()
    print("  leaf flow classes that no entry constructs (%d):" % len(leaves))
    for t in sorted(leaves):
        # OffspringFlow -> offspring
        guess = t[: -len("Flow")]
        guess = guess[:1].lower() + guess[1:]
        note = "  <- module '%s' exists and is registered as something else" % guess if guess in ids else ""
        print("    %-22s (%s)%s" % (t, declared[t][1], note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
