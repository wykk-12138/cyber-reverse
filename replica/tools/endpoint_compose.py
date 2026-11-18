"""Which endpoints that endpoint_coverage.py calls "missing" are reachable by literal concatenation?

WHY THIS EXISTS (and why it is not a rewrite of endpoint_coverage.py):
endpoint_coverage.py counts a path as covered only when the quoted literal "<path>" occurs in
source. Flows here compose URLs from a base plus a path -- GoatFlow builds
`Origin(c.Url) + "/web-api" + path` and then passes "/v1/addresses" -- so an endpoint that is
genuinely implemented never appears as one quoted literal and is counted missing.

A bare substring test cannot fix this: R1117 showed it counts comment text as implementation. So
this tool works on *code only* (line and block comments stripped) and requires the missing path to
be splittable into two segments that each occur as a QUOTED literal in that code. That models the
composition the source actually performs instead of hoping a name shows up somewhere.

It reports a second, explained number. The conservative figure from endpoint_coverage.py stays as
it is; this is an additive reading, not a replacement.
"""
import io
import os
import re
import subprocess
import sys

REPLICA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPLICA, "src")

COMMENT_LINE = re.compile(r"//.*$", re.M)
COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.S)
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')


def code_only(text):
    """Drop // and /* */ comments. String literals survive, including any // inside them."""
    out = []
    i = 0
    n = len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def literals():
    found = set()
    for root, _dirs, names in os.walk(SRC):
        for name in names:
            if not name.endswith(".cs"):
                continue
            path = os.path.join(root, name)
            try:
                body = io.open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in QUOTED.finditer(code_only(body)):
                found.add(m.group(1))
    return found


def splittable(path, lits):
    """Is `path` two adjacent quoted literals the source actually carries?"""
    for i in range(2, len(path) - 1):
        head, tail = path[:i], path[i:]
        if head in lits and tail in lits:
            return head, tail
    return None


def main():
    out = subprocess.run([sys.executable, os.path.join(REPLICA, "tools", "endpoint_coverage.py"), "-v"],
                         capture_output=True, text=True, cwd=REPLICA,
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"}).stdout
    missing = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] in ("store", "vendor", "hostless"):
            missing.append((parts[0], parts[2]))

    lits = literals()
    composed, unresolved = [], []
    for key, path in missing:
        probe = path.split("?")[0].split("{")[0]
        hit = splittable(probe, lits)
        (composed if hit else unresolved).append((key, path, hit))

    print("endpoint_coverage reported missing: %d" % len(missing))
    print("reachable by literal concatenation: %d" % len(composed))
    for key, path, hit in composed:
        print("   COMPOSED %-7s %-60s = %r + %r" % (key, path[:60], hit[0], hit[1]))
    print("still unexplained: %d" % len(unresolved))
    for key, path, _ in unresolved:
        print("   OPEN     %-7s %s" % (key, path[:80]))


if __name__ == "__main__":
    main()
