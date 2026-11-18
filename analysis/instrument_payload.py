# WHY THIS EXISTS: the payload's frame array and its opcode stream live entirely inside its own
# closure, so no shim hook can observe them. The one workable seam is a probe inserted into a COPY of
# the fixture (the original under tests/Cybersole.Tests/fixtures/nike-p.js is never modified).
#
# What it emits: for every dispatch, one row capturing the program counter, the frame length, and the
# type of slots 2..7 — enough to see which slot a call instruction reads and whether it was ever
# written. It also records every opcode-81 read (the payload's "load a global by name" instruction),
# which is how a missing host API shows up as `undefined` in a call slot.
#
# Usage:  python analysis/instrument_payload.py
#         -> writes tests/Cybersole.Tests/fixtures/nike-p-traced.js (inside replica/)
# The generated file is a build artifact; do not commit it.
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p.js")
DST = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p-traced.js")

ANCHOR = "var T,E;var i=void 0;"

PROBE = (
    "var T,E;var i=void 0;"
    "if(window.__dshFrames&&window.__dshFrames.length<1000){"
    "var __q=function(v){return v===void 0?'undef':v===null?'null':typeof v==='function'?'fn':"
    "typeof v==='object'?(Array.isArray(v)?'arr'+v.length:'obj'):typeof v+':'+String(v).slice(0,10)};"
    "window.__dshFrames.push([e.m[0],e.m.length,__q(e.m[2]),__q(e.m[3]),__q(e.m[4]),"
    "__q(e.m[5]),__q(e.m[6]),__q(e.m[7])]);"
    # opcode 81 is `a(n, i[0][e(n)])` — read a global by name. Log the name it asked for.
    "if(t[e.m[0]]===81&&window.__dshGlobals&&window.__dshGlobals.length<400){"
    "window.__dshGlobals.push(String(e.m[e.m[0]+1]));"
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
