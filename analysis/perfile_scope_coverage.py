"""Does `bind_diff --per-file` actually check anything? (R583)

`bind_diff --per-file` printed `missing: 0` over 174 types and 819 members. That looks like a perfect score, but
the tool has this shape (bind_diff.py lines 42-46):

    scope = by_class.get(simple)
    if not scope:
        rows.append((typ, len(members), None, members))
        continue                            # <- not counted in missing_total

So a type whose body the tool cannot locate contributes **nothing**: its members are neither found nor missing. A
"0" produced that way means "nothing was checked", not "everything is present".

This measures how many of the 174 contract types the per-file scope can actually locate, using the same
`by_class`-style keying, and separately how many it can locate when positional records are included (the blind spot
R580 found in `bind_scope.DECL` and R582 found in my own coverage tool).

Read-only.
"""

import glob
import io
import json
import os
import re

REPO = r"D:\projects\cyber-reverse\replica"
BIND = os.path.join(REPO, "docs", "xaml_bindings.json")

# the shape bind_diff uses: a body is the text inside the class's braces
CLASS_BRACE = re.compile(r"\bclass\s+(\w+)\s*(?::[^{]*)?\{")
# the broader shape: any type declaration, with or without a brace body
ANY_DECL = re.compile(r"\b(?:class|interface|record|struct|enum)\s+(\w+)")
NAMESPACE = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)


def scan(pattern, include_positional):
    found = set()
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        if include_positional:
            for d in ANY_DECL.finditer(text):
                found.add(d.group(1))
        else:
            for d in pattern.finditer(text):
                found.add(d.group(1))
    return found


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    names = [t.split(".")[-1].split("`")[0] for t in binds]

    narrow = scan(CLASS_BRACE, False)
    broad = scan(None, True)

    narrow_hit = [n for n in names if n in narrow]
    broad_hit = [n for n in names if n in broad]

    print("contract types                          : %d" % len(set(names)))
    print("locatable by a `class X ... {` body     : %d  <- what --per-file can see" % len(set(narrow_hit)))
    print("locatable by any type declaration       : %d" % len(set(broad_hit)))
    print()
    print("contract types invisible to --per-file  : %d" % (len(set(names)) - len(set(narrow_hit))))

    missing_from_narrow = sorted(set(n for n in names if n not in narrow))
    print()
    print("=== the first 20 types --per-file cannot locate (so it reports nothing about them) ===")
    for n in missing_from_narrow[:20]:
        print("   " + n)


if __name__ == "__main__":
    main()
