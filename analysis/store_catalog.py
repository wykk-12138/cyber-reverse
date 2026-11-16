"""Extract the replica's store catalogue structurally. (R758)

Criterion (f) asks for a recomputable coverage table: the original's store list (taken from the binary) against the
replica's dispatch table. This is the replica half.

R757 counted substrings in the source and got a confusing list -- step names such as `supreme-add` and `raffle-monitor`
came out alongside store slugs. That is exactly why substring counts are a map and not a verdict. This reads the
declarations instead: every `: StoreModuleBase` subclass declares `Id`, `Name` and `Domains`, so the table can be
derived from structure rather than from word frequency.

**Why not an existing tool** (AGENTS.md §1.2): the question is about this repo's own C# declarations, not about the
target binary, so none of the reverse-engineering tooling applies. `bind_diff.py` compares the *target's* binding table
against the replica; it does not read module declarations.
"""

import io
import os
import re
import sys

STORES = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores"


def module_blocks(text):
    """Yield (class name, block text) for every StoreModuleBase subclass."""
    for m in re.finditer(r"class\s+(\w+)\s*:\s*StoreModuleBase\b", text):
        start = text.find("{", m.end())
        if start < 0:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    yield m.group(1), text[start:i + 1]
                    break


def field(block, name):
    m = re.search(r'override\s+string\s+' + name + r'\s*=>\s*"([^"]*)"', block)
    return m.group(1) if m else None


def domains(block):
    m = re.search(r"override\s+IReadOnlyList<string>\s+Domains\s*=>[^;]*;", block, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(0))


def main():
    rows = []
    for dirpath, dirnames, filenames in os.walk(STORES):
        if "obj" in dirpath or "bin" in dirpath:
            continue
        for name in sorted(filenames):
            if not name.endswith(".cs"):
                continue
            path = os.path.join(dirpath, name)
            text = io.open(path, encoding="utf-8", errors="replace").read()
            for cls, block in module_blocks(text):
                rows.append({
                    "class": cls,
                    "id": field(block, "Id") or "?",
                    "name": field(block, "Name") or "?",
                    "domains": domains(block),
                    "file": os.path.relpath(path, STORES),
                })

    rows.sort(key=lambda r: r["id"])
    print("  modules: %d" % len(rows))
    print()
    print("  %-22s %-20s %-40s %s" % ("id", "name", "domains", "class"))
    print("  " + "-" * 108)
    for r in rows:
        print("  %-22s %-20s %-40s %s" % (
            r["id"], r["name"][:20], (", ".join(r["domains"]) or "(none)")[:40], r["class"]))

    # a module without a domain cannot be reached by host, which is worth flagging
    bare = [r for r in rows if not r["domains"]]
    print()
    print("  modules with no domain: %d%s" % (len(bare), " -- " + ", ".join(r["id"] for r in bare) if bare else ""))
    dupes = {}
    for r in rows:
        for d in r["domains"]:
            dupes.setdefault(d, []).append(r["id"])
    shared = {d: ids for d, ids in dupes.items() if len(ids) > 1}
    print("  domains claimed by more than one module: %d" % len(shared))
    for d, ids in sorted(shared.items()):
        print("    %-36s %s" % (d, ", ".join(ids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
