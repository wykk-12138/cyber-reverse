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


def compose(path, lits, max_parts=3):
    """Return a tuple of 2..max_parts quoted literals that concatenate to `path`, or None.

    R1125: the first version tried two segments only, which left every three-part composition in the
    "unexplained" bucket and made that number an upper bound without saying so. The search is the same
    idea generalised -- still only literals that the source actually carries, never a fuzzy substring.
    """
    best = []

    def dfs(start, parts):
        if best:
            return
        if start == len(path):
            if len(parts) >= 2:
                best.extend(parts)
            return
        if len(parts) >= max_parts:
            return
        for end in range(start + 1, len(path) + 1):
            seg = path[start:end]
            # R1125: a one-character segment ('/' or '.') proves nothing -- it would let almost any
            # path be "explained" by generic fragments lying around the source. Every segment has to
            # carry real path text before the concatenation is admitted as evidence.
            if len(seg) < 2:
                continue
            if seg in lits:
                dfs(end, parts + [seg])

    dfs(0, [])
    return tuple(best) if best else None


def embedded(path, lits):
    """Is `path` carried by a longer quoted literal, anchored at one end?

    R1125: this is the third blind spot. PayPal's 3DS paths live in single literals that already
    include the host ("https://www.paypal.com/payment-authentication/threeds/v1/init-method"), so they
    match neither the bare-quoted test nor a two-part split. Anchoring at the start or the end keeps
    this precise: an arbitrary substring hit is exactly the R1117 mistake.
    """
    for lit in lits:
        # R1125: a prose description literal can end with a path and would pass the anchor test --
        # three "tokenise endpoint not captured ..." notes did exactly that. A URL never contains a
        # space, so requiring one is enough to separate a real endpooint literal from a sentence.
        if " " in lit:
            continue
        if len(lit) > len(path) and (lit.endswith(path) or lit.startswith(path)):
            return lit
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
    composed, embedded_rows, unresolved = [], [], []
    for key, path in missing:
        probe = path.split("?")[0].split("{")[0]
        hit = compose(probe, lits)
        if hit:
            composed.append((key, path, hit))
            continue
        anchor = embedded(probe, lits)
        (embedded_rows if anchor else unresolved).append((key, path, anchor))

    two = sum(1 for _, _, h in composed if len(h) == 2)
    three = sum(1 for _, _, h in composed if len(h) == 3)
    print("endpoint_coverage reported missing: %d" % len(missing))
    print("reachable by literal concatenation: %d  (two-part %d, three-part %d)"
          % (len(composed), two, three))
    for key, path, hit in composed:
        print("   COMPOSED %-7s %-58s = %s" % (key, path[:58], " + ".join(repr(p) for p in hit)))
    print("carried by a longer anchored literal: %d" % len(embedded_rows))
    for key, path, lit in embedded_rows:
        print("   EMBEDDED %-7s %-58s in %r" % (key, path[:58], lit[:70]))
    print("still unexplained: %d" % len(unresolved))
    for key, path, _ in unresolved:
        print("   OPEN     %-7s %s" % (key, path[:80]))


if __name__ == "__main__":
    main()
