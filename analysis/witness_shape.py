"""Classify all 129 witness candidates as wiring or logic, by the shape of their decompilation. (R730)

**Why this exists** (project convention §1.2): R721 found that the app-string set is dominated by UI state-refresh code
whose "behaviour" is a property assignment, and R729's next candidate (0x14125fc80) turned out to be a 22-entry object
initialiser with forty locals. Picking candidates one at a time and discovering this after decompiling is wasteful.
No existing tool ranks functions by whether they are wiring: `rea`'s matching compares functions, it does not classify
their purpose, and `ida_pro_mcp` exposes decompilation but no such heuristic.

**Criterion, fixed before measuring**: decompile each candidate and count how many of its distinct callees belong to the
Avalonia property/binding helper families (`sub_14302xxx`, `sub_143028C10`, `sub_143028E70`, `sub_142E7xxxx`) against
its total distinct callees.

    share >= 40%   wiring   -- mostly property plumbing
    share <  40%   logic    -- mostly other work

The 40% line is a choice and is labelled as one. What the table is for is ordering, not judging: a function at 38% is
not meaningfully different from one at 42%, but one at 8% is worth reading before one at 55%.
"""

import io
import json
import re
import sys
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
CAND = r"D:\projects\cyber-reverse\analysis\witness_candidates.txt"
OUT = r"D:\projects\cyber-reverse\analysis\witness_candidate_shape.tsv"
_id = [0]

WIRING = re.compile(r"^(sub_14302\w+|sub_142E7\w+|sub_143028C10|sub_143028E70)$")
ANY_CALLEE = re.compile(r"\b(sub_[0-9A-Fa-f]{6,}|off_[0-9A-Fa-f]{6,})\b")


def rpc(method, params=None, timeout=120):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def decompile(addr):
    res = rpc("tools/call", {"name": "decompile", "arguments": {"addr": addr, "max_lines": 2500}})
    return json.loads(res["result"]["content"][0]["text"])


def main():
    rows = []
    for line in io.open(CAND, encoding="utf-8"):
        if line.startswith("#"):
            continue
        parts = line.rstrip().split("\t")
        addr = parts[0]
        # R730: witness_candidates.txt writes bare hex with no 0x prefix. Passing "14125fc80" to the decompiler
        # gets it read as decimal, which lands nowhere and returns empty code -- and an empty body is skipped
        # below, so the whole table came back with zero rows and no error.
        if not addr.startswith("0x"):
            addr = "0x" + addr
        rows.append((addr, int(parts[1]) if len(parts) > 1 else 0))

    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "shape", "version": "1"}})

    out = []
    for i, (addr, size) in enumerate(rows, 1):
        try:
            d = decompile(addr)
        except Exception as e:
            print("  %-12s decompile failed: %s" % (addr, e))
            continue
        code = d.get("code") or ""
        callees = set(ANY_CALLEE.findall(code))
        callees.discard("sub_" + addr[2:].upper())
        if not callees:
            continue
        wiring = sum(1 for c in callees if WIRING.match(c))
        share = 100.0 * wiring / len(callees)
        out.append((share, addr, size, len(callees), len(code.splitlines())))
        if i % 20 == 0:
            print("  ... %d / %d" % (i, len(rows)))

    out.sort()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# witness candidates by wiring share (R730)\n")
        fh.write("wiring_pct\taddr\tsize\tcallees\tpseudocode_lines\n")
        for share, addr, size, ncal, nlines in out:
            fh.write("%.1f\t%s\t%d\t%d\t%d\n" % (share, addr, size, ncal, nlines))

    logic = [r for r in out if r[0] < 40]
    print()
    print("classified           : %d" % len(out))
    print("logic  (< 40%% wiring): %d" % len(logic))
    print("wiring (>= 40%%)      : %d" % (len(out) - len(logic)))
    print()
    print("the twelve most logic-like:")
    for share, addr, size, ncal, nlines in logic[:12]:
        print("  %-12s wiring=%5.1f%%  size=%-6d callees=%-3d lines=%d" % (addr, share, size, ncal, nlines))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
