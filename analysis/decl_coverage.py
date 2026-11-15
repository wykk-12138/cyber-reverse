"""Before trusting declaration-level matching, measure how often it is ambiguous. (R658)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); this reads the
replica's source and the contract, both local.

**Why measure first**: R657 added a comment rule to the triage and it produced one correct verdict and one false
positive in the same run. The lesson recorded was to measure a criterion's false-positive rate **before** trusting it,
not after. So this does that for the next candidate -- matching by **declared** members alone, ignoring the comment.

**Definition, fixed before measuring**:

  * a class **covers** a contract when every contract member appears in that class as a declaration
    (`public|internal <type> <name> {` / `=>` / `;` / `=`), not merely as a name in the body;
  * a contract is **DISCRIMINATIVE** when exactly **one** class covers it;
  * **AMBIGUOUS** when two or more do -- the criterion cannot name a single answer, so any verdict built on it would
    be a guess;
  * **NONE** when nothing covers it.

Reported per contract, so the ambiguity rate is visible before anything is changed.

Read-only. Prints; writes nothing.
"""

import io
import json
import os
import re
import sys

SRC = r"D:\projects\cyber-reverse\replica\src"
BINDINGS = r"D:\projects\cyber-reverse\analysis\xaml_bindings.json"

DECL = re.compile(r"\b(?:class|record|struct|interface)\s+(\w+)\s*(?:<[^>]*>)?\s*(?:\([^)]*\))?\s*(?::[^{]+)?\{")


def bodies():
    found = {}
    for dirpath, _dirnames, filenames in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".cs"):
                continue
            text = io.open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
            for m in DECL.finditer(text):
                brace = m.end() - 1
                depth, i = 0, brace
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                found.setdefault(m.group(1), []).append((fn, text[brace:i + 1]))
    return found


def covers(body, members):
    for mem in members:
        if not re.search(r"\b(?:public|internal)\s+[\w<>?\[\],. ]+\s+%s\s*(?:\{|=>|;|=)" % re.escape(mem), body):
            return False
    return True


def main():
    contract = json.load(io.open(BINDINGS, encoding="utf-8"))
    all_bodies = bodies()
    print("contract types: %d   declared class names in src: %d" % (len(contract), len(all_bodies)))
    print()

    # only the ones the triage classifies as absent
    triage = io.open(r"D:\projects\cyber-reverse\docs\TYPE_PRESENCE_TRIAGE.md", encoding="utf-8").read()
    absent = set()
    for line in triage.splitlines():
        m = re.match(r"\|\s*`(\w+)`\s*\|", line)
        if m:
            absent.add(m.group(1))

    rows = []
    for full, members in sorted(contract.items()):
        simple = full.rsplit(".", 1)[-1]
        if simple not in absent:
            continue
        cands = []
        for name, sites in all_bodies.items():
            for fn, body in sites:
                if covers(body, members):
                    cands.append(name)
                    break
        kind = "DISCRIMINATIVE" if len(cands) == 1 else ("NONE" if not cands else "AMBIGUOUS")
        rows.append((simple, len(members), kind, sorted(set(cands))))

    print("=== the %d contract types the triage calls absent ===" % len(rows))
    for simple, n, kind, cands in rows:
        show = ", ".join(cands[:5]) + (" …" if len(cands) > 5 else "")
        print("  %-28s %d member(s)  %-14s %s" % (simple, n, kind, show or "-"))

    import collections
    tally = collections.Counter(k for _s, _n, k, _c in rows)
    print()
    print("tally: %s" % dict(tally))
    disc = [s for s, _n, k, _c in rows if k == "DISCRIMINATIVE"]
    amb = [s for s, _n, k, _c in rows if k == "AMBIGUOUS"]
    print()
    print("declaration matching would name a single answer for %d of %d" % (len(disc), len(rows)))
    if amb:
        print("ambiguous (would be a guess): %s" % amb)


if __name__ == "__main__":
    sys.exit(main())
