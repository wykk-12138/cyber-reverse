# WHY THIS EXISTS: the payload's frame array `m` lives only inside its own closure, so shim hooks cannot
# see it. This writes an instrumented COPY of the fixture (the original is never modified) with a probe
# that records every CHANGE of slots 5..7, together with the program counter and opcode that caused it.
# That history is what shows whether slot 5 is ever written, and by which instruction.
#
# Usage:  python analysis/instrument_payload.py
#         -> writes replica/tests/Cybersole.Tests/fixtures/nike-p-traced.js (a build artifact, not committed)
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p.js")
DST = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p-traced.js")

ANCHOR = "var T,E;var i=void 0;"

PROBE = (
    "var T,E;var i=void 0;"
    "if(window.__dshTrace){"
    "var __q=function(v){return v===void 0?'undef':v===null?'null':typeof v==='function'?'fn':"
    "typeof v==='object'?(Array.isArray(v)?'arr'+v.length:'obj'):typeof v+':'+String(v).slice(0,10)};"
    "var __s=__q(e.m[5])+'|'+__q(e.m[6])+'|'+__q(e.m[7]);"
    "if(window.__dshLast!==__s){window.__dshLast=__s;"
    "if(window.__dshTrace.length<1000)window.__dshTrace.push([e.m[0],t[e.m[0]],__s]);}"
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
