"""For each of the copy gaps, show the original text beside the closest thing the source has (R543).

`copy_audit_report.py` now says 19 keys are absent. A count is not a diagnosis: some of those are long tooltips
whose meaning may already be implemented in shorter words, others may be genuinely unimplemented, and a few
will be the audit's own `[^"\\n]` limits showing through again on a *different* pattern.

So for every absent key this prints:

    original text
    the closest source literal (difflib ratio), or nothing
    the source file it came from

Read-only. The point is to sort 19 rows into "write the real sentence", "already says it differently, leave it",
and "the page does not exist".
"""

import io
import os
import re
import difflib

POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
SRC = r"D:\projects\cyber-reverse\replica\src"

PAT = re.compile(r'"([A-Z][\w.]*\.[\w.]+)":\s*"((?:[^"\\\n]|\\.){1,400})"')


def main():
    raw = io.open(POOL, encoding="utf-8", errors="replace").read()
    pairs = sorted(set(
        (m.group(1), m.group(2).replace('\\"', '"').replace('\\\\', '\\'))
        for m in PAT.finditer(raw)))

    literals = []          # (text, file)
    joined = []
    for dirpath, _d, files in os.walk(SRC):
        if os.sep + "obj" in dirpath or os.sep + "bin" in dirpath:
            continue
        for fn in files:
            if not fn.endswith(".cs"):
                continue
            path = os.path.join(dirpath, fn)
            body = io.open(path, encoding="utf-8", errors="replace").read()
            joined.append(body)
            for m in re.finditer(r'"([^"\\\n]{6,400})"', body):
                literals.append((m.group(1), fn))

    haystack = "\n".join(joined)

    print("absent keys: probing %d pool pairs" % len(pairs))
    print()
    absent = 0
    for key, value in pairs:
        if value in haystack:
            continue
        absent += 1
        best, best_ratio, best_file = None, 0.0, None
        for lit, fn in literals:
            r = difflib.SequenceMatcher(None, value.lower(), lit.lower()).ratio()
            if r > best_ratio:
                best, best_ratio, best_file = lit, r, fn
        print("%-46s %s" % (key, "ABSENT"))
        print("    original : %s" % value[:150])
        if best and best_ratio >= 0.55:
            print("    closest  : %s" % best[:150])
            print("    ratio    : %.2f   in %s" % (best_ratio, best_file))
        else:
            print("    closest  : (nothing above 0.55)")
        print()

    print("total absent: %d" % absent)


if __name__ == "__main__":
    main()
