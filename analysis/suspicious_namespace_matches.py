"""Among the 65 namespace-mismatched "present" types, which look like a DIFFERENT type? (R582)

R581 measured the split (92 same-namespace / 65 different / 17 nowhere) and established that requiring namespace
equality would be wrong: most of the 65 are the same type placed in `Cybersole.Core.Models` instead of
`Cybersole.Models`. But `State` was a genuine mis-match, so the 65 are not uniformly benign.

This separates them mechanically. Two namespace strings are compared after dropping a `Core` segment and ignoring a
trailing `Modals`, then the **semantic domain** is the first segment that differs:

    Cybersole.Models.Profile        -> Cybersole.Core.Models.Profile      only `Core` inserted   -> rename
    Cybersole.Ui.Views.Tasks.Modals -> Cybersole.Ui.Views.Tasks           `Modals` dropped       -> rename
    Cybersole.Models.Notification   -> Cybersole.Services.Notification    Models -> Services     -> SUSPICIOUS
    Cybersole.Models.State          -> Cybersole.Stores.Scripts.State     Models -> Stores       -> SUSPICIOUS

"Suspicious" means *the same name appears in an unrelated part of the program*, which is exactly how `State` turned
out. It is a screen, not a verdict: each hit still has to be read.

Read-only.
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

# segments that carry no meaning about what the type IS
NOISE = {"core", "modals"}


def declarations():
    by_name = {}
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        m = NS.search(text)
        ns = m.group(1) if m else ""
        for d in DECL.finditer(text):
            by_name.setdefault(d.group(1), set()).add(ns)
    return by_name


def meaningful(ns):
    return [s for s in ns.split(".") if s.lower() not in NOISE]


def classify(contract_ns, actual_ns):
    a, b = meaningful(contract_ns), meaningful(actual_ns)
    if a == b:
        return "rename", "只有层级移动"
    # longest common prefix of segments
    common = 0
    for x, y in zip(a, b):
        if x == y:
            common += 1
        else:
            break
    a_rest = a[common:]
    b_rest = b[common:]
    if not a_rest or not b_rest:
        return "rename", "一方是另一方的前缀"
    return "suspicious", "%s -> %s" % (a_rest[0], b_rest[0])


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    by_name = declarations()

    rows = []
    for full in sorted(binds):
        parts = full.split(".")
        ns = ".".join(parts[:-1])
        simple = parts[-1].split("`")[0]
        actual = by_name.get(simple)
        if not actual:
            continue
        if ns in actual:
            continue                      # same namespace: not this report's business
        for got in sorted(actual):
            verdict, reason = classify(ns, got)
            rows.append((verdict, full, ns, got, reason))

    rename = [r for r in rows if r[0] == "rename"]
    suspicious = [r for r in rows if r[0] == "suspicious"]

    print("mismatched types examined : %d" % len(rows))
    print("  rename (level move only): %d" % len(rename))
    print("  suspicious (domain moved): %d" % len(suspicious))

    print()
    print("=== suspicious: same name, unrelated part of the program ===")
    for _v, full, ns, got, reason in suspicious:
        print("  %-52s %-30s -> %-34s  %s" % (full, ns, got, reason))

    print()
    print("=== rename (for contrast, first 10) ===")
    for _v, full, ns, got, reason in rename[:10]:
        print("  %-52s %-30s -> %-34s  %s" % (full, ns, got, reason))


if __name__ == "__main__":
    main()
