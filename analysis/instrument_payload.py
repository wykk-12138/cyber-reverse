# WHY THIS EXISTS: payload frame slots live only inside the payload's closure, so an instrumented COPY of
# the fixture is written (original untouched). This version records two things needed to explain the one
# call whose callee slot is undefined (pc 69469):
#   1. every change of slot 5, with the pc and opcode that caused it      -> which instruction writes it
#   2. every opcode-81 global read with its target slot                   -> whether a missing global feeds it
#
# Usage: python analysis/instrument_payload.py
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p.js")
DST = os.path.join(ROOT, "replica", "tests", "Cybersole.Tests", "fixtures", "nike-p-traced.js")

ANCHOR = "var T,E;var i=void 0;"

PROBE = (
    "var T,E;var i=void 0;"
    "if(window.__dshM5){"
    "var __p=e.m[0],__op=t[__p];"
    "var __v=e.m[5];"
    "if(window.__dshM5.last!==__v){"
    "window.__dshM5.last=__v;"
    "if(window.__dshM5.log.length<600)"
    "window.__dshM5.log.push([__p,__op,__v===void 0?'UNDEF':(typeof __v==='function'?'fn':typeof __v)]);"
    "}"
    "if(__op===81&&window.__dshG&&window.__dshG.length<400){"
    "window.__dshG.push([__p,t[__p+1],t[__p+2],t[__p+3],t[__p+4]]);"
    "}"
    "}"
)


def main():
    src = io.open(SRC, encoding="utf-8").read()
    if ANCHOR not in src:
        raise SystemExit("anchor %r not found" % ANCHOR)
    out = src.replace(ANCHOR, PROBE, 1)
    if out == src:
        raise SystemExit("probe not inserted")
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", DST, "delta", len(out) - len(src))


if __name__ == "__main__":
    main()
