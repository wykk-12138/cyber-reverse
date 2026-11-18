# WHY THIS EXISTS: the payload's frame array and dispatch state are only visible from inside its own
# closure. This writes an instrumented COPY of the fixture (the original is never modified) that keeps a
# rolling window of the last dispatches and snapshots it whenever a call instruction is about to run.
# Comparing the window before a call whose callee slot is undefined against one whose callee is present
# shows which instruction was skipped or jumped over.
#
# Usage:  python analysis/instrument_payload.py
#         -> writes replica/tests/Cybersole.Tests/fixtures/nike-p-traced.js (build artifact, not committed)
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p.js")
DST = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p-traced.js")

ANCHOR = "var T,E;var i=void 0;"

PROBE = (
    "var T,E;var i=void 0;"
    "if(window.__dshRing){"
    "var __op=t[e.m[0]];"
    "if(__op===12){"
    "if(e.m[5]===void 0&&window.__dshFail.length<8)window.__dshFail.push(window.__dshRing.slice());"
    "else if(e.m[5]!==void 0&&window.__dshOk.length<4)window.__dshOk.push(window.__dshRing.slice());"
    "}"
    "window.__dshRing.push([e.m[0],__op]);"
    "if(window.__dshRing.length>45)window.__dshRing.shift();"
    "}"
)


def main():
    src = io.open(SRC, encoding="utf-8").read()
    if ANCHOR not in src:
        raise SystemExit("anchor %r not found in %s" % (ANCHOR, SRC))
    out = src.replace(ANCHOR, PROBE, 1)
    if out == src:
        raise SystemExit("probe was not inserted")
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", DST)
    print("size", len(out), "delta", len(out) - len(src))


if __name__ == "__main__":
    main()
