import io
p = r"D:\projects\cyber-reverse\replica\tools\bind_scope.py"
code = '''"""Type-scoped binding check (R342, extraction fixed in R343).

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

DECL = re.compile(r"\\b(?:class|interface|record|struct)\\s+(\\w+)[^;{]*\\{")


def bodies_by_name():
    """Every declaration's body text, keyed by short type name."""
    found = {}
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
                            break
    return found


def main():
    binds = json.load(io.open(BINDS, encoding="utf-8"))
    bodies = bodies_by_name()

    rows = []
    for full, members in sorted(binds.items()):
        short = full.split(".")[-1]
        parts = bodies.get(short)
        if not parts:
            continue                          # type absent: the other metric's business
        merged = "\\n".join(parts)
        missing = [m for m in sorted(members)
                   if re.search(r"\\b" + re.escape(m) + r"\\b", merged) is None]
        if missing:
            rows.append((short, missing))

    print("type-scoped check: types present, members missing on THAT type")
    for short, missing in rows:
        print("  %-28s %s" % (short, ", ".join(missing)))
    print("types with scope misses:", len(rows))


if __name__ == "__main__":
    main()
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('bind_scope.py rewritten with brace matching')
