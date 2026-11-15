"""How many "present" contract types are matched by simple name into the WRONG namespace? (R581)

`bind_diff --type-presence` decides presence with `typ.split('.')[-1].split('`')[0] in declared`, where `declared`
is a flat set of names scraped from `class|record|struct|enum|interface`. Namespace is thrown away.

R580's counters led to `Cybersole.Models.State`: the contract binds `Name` on it, the replica has no such type, but
it has an enum called `State` in `Cybersole.Stores.Scripts`. The simple-name match says "present"; the namespaces
disagree.

This measures how often that happens, by rebuilding `declared` as (namespace, name) pairs and asking, for each
contract type:

    is there a declaration of the same simple name inside the contract's own namespace?

If not, the type is a **false positive of the simple-name heuristic** — counted present, actually unmatched.

Read-only; nothing is changed.
"""

import glob
import io
import json
import os
import re

REPO = r"D:\projects\cyber-reverse\replica"
BIND = os.path.join(REPO, "docs", "xaml_bindings.json")

NS = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
DECL = re.compile(r"\b(?:class|interface|record|struct|enum)\s+(\w+)")


def declarations_with_namespaces():
    """(namespace, simple name) pairs, plus a name -> set(namespaces) index."""
    pairs = set()
    by_name = {}
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        m = NS.search(text)
        ns = m.group(1) if m else "(file-scoped-missing)"
        for d in DECL.finditer(text):
            name = d.group(1)
            pairs.add((ns, name))
            by_name.setdefault(name, set()).add(ns)
    return pairs, by_name


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    pairs, by_name = declarations_with_namespaces()

    print("contract types            : %d" % len(binds))
    print("distinct (ns,name) pairs  : %d" % len(pairs))

    same_ns = []
    wrong_ns = []
    missing = []

    for full in sorted(binds):
        parts = full.split(".")
        ns = ".".join(parts[:-1])
        simple = parts[-1].split("`")[0]
        if (ns, simple) in pairs:
            same_ns.append(full)
        elif simple in by_name:
            wrong_ns.append((full, ns, sorted(by_name[simple])))
        else:
            missing.append(full)

    print()
    print("declared in the SAME namespace as the contract : %d" % len(same_ns))
    print("declared only in a DIFFERENT namespace         : %d" % len(wrong_ns))
    print("not declared anywhere                          : %d" % len(missing))

    if wrong_ns:
        print()
        print("=== false positives of the simple-name match ===")
        for full, want_ns, got in wrong_ns:
            print("  %-46s  contract ns=%-28s  found in: %s"
                  % (full, want_ns, ", ".join(got[:3])))

    if missing:
        print()
        print("=== declared nowhere ===")
        for full in missing:
            print("  " + full)


if __name__ == "__main__":
    main()
