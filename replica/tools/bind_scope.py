"""Type-scoped binding check (R342, extraction fixed in R343).

The name-level metric in bind_diff.py is satisfied when a member name appears anywhere in the repository, which hides
"the member is on some other type". This script asks the narrower question: for every type that exists in the replica,
is each member the binding table binds on it declared *inside that type's body*?

Bodies are found by brace matching from the declaration's opening brace, so nesting no longer decides the answer.
Base-class members still count as missing (the script is a screener, not a verdict) - each hit has to be read by hand.
"""

import io
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")
SRC = os.path.join(ROOT, "src")

DECL = re.compile(r"\b(?:class|interface|record|struct)\s+(\w+)\s*(?::\s*([^;{]+?))?\s*(?:where[^;{]*)?\{")


def bodies_by_name():
    """Every declaration's body text, keyed by short type name."""
    found = {}
    bases = {}
    for dirpath, _dirnames, filenames in os.walk(SRC):
        if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
            continue
        for filename in filenames:
            if not filename.endswith(".cs"):
                continue
            text = io.open(os.path.join(dirpath, filename), encoding="utf-8", errors="replace").read()
            for match in DECL.finditer(text):
                depth = 0
                start = match.end() - 1          # at the '{'
                for index in range(start, len(text)):
                    if text[index] == "{":
                        depth += 1
                    elif text[index] == "}":
                        depth -= 1
                        if depth == 0:
                            found.setdefault(match.group(1), []).append(text[start:index + 1])
                            bases.setdefault(match.group(1), []).extend(
                                b.split(".")[-1].split("<")[0].strip()
                                for b in (match.group(2) or "").split(",")
                                if b.strip())
                            break
    return found, bases


def main():
    binds = json.load(io.open(BINDS, encoding="utf-8"))
    bodies, bases = bodies_by_name()

    def with_bases(name, seen=None):
        """The type's body plus every ancestor's — members inherited from a base are not missing."""
        seen = seen or set()
        if name in seen:
            return ""
        seen.add(name)
        text = "\n".join(bodies.get(name, []))
        for base in bases.get(name, []):
            text += "\n" + with_bases(base, seen)
        return text

    rows = []
    examined = 0
    skipped_generic = 0
    for full, members in sorted(binds.items()):
        short = full.split(".")[-1]
        parts = bodies.get(short)
        if not parts:
            # R580: distinguish "no such type" from "the type exists but this key carries a generic-arity
            # suffix". Only the second is a blind spot of this tool, and without the count it is invisible:
            # a type that drops out of the loop leaves `types with scope misses` at 0.
            if "`" in short:
                skipped_generic += 1
            continue                          # type absent: the other metric's business
        examined += 1
        merged = with_bases(short)
        missing = [m for m in sorted(members)
                   if re.search(r"\b" + re.escape(m) + r"\b", merged) is None]
        if missing:
            rows.append((short, missing))

    print("type-scoped check: types present, members missing on THAT type")
    for short, missing in rows:
        print("  %-28s %s" % (short, ", ".join(missing)))
    print("types with scope misses:", len(rows))
    # R580: how many types this run actually looked at. A drop here means the DECL regex stopped matching some
    # declaration form -- the failure this tool could previously hide.
    print("types examined:", examined)
    print("types skipped for generic arity:", skipped_generic)
    print("note: base-class inheritance is counted (by design since R343)")


if __name__ == "__main__":
    main()
