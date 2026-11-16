"""Rank candidate functions by how many places call them. (R719)

**Why this exists** (project convention §1.2): R718 built fifteen behaviour probes whose expectations come from
decompilation, but it does not answer "which function next". Probing all ~187,000 functions one assertion at a time is
not a plan. No existing tool ranks by inbound references: the plugin exposes `xref_query` (one address at a time),
`func_profile` (summary metrics for a caller-supplied list) and `export_funcs` (what `func_compare.py` already uses),
and `rea`'s comparison tools need a provider this host does not have.

**Why now**: the next probe's value is proportional to how much behaviour it covers, and a function called from fifty
places is a better witness than one called from none.

**Method**: one `py_eval` pass over `idautils.Functions()` counting `idautils.XrefsTo(ea, 0)`. That is one call per
function, so it is bounded by the plugin's 60-second budget -- hence the paging below. Results are merged across pages
and written to `analysis/caller_ranking.tsv`.

**Criterion, fixed before measuring**: the ranking is only usable if the sampled pages together cover every function
the run claims to cover, and if a spot check of three addresses reproduces their counts through the independent
`xref_query` tool. A count that only this script can produce is not evidence.

**R719 VERDICT -- the criterion is WRONG, and this tool is kept as the record of why.** On a 6,000-function sample the
top fifteen by caller count are all unnamed functions of 4 to 288 bytes called 700 to 4,000 times:

    0x1400fe270  callers=4046  size=97      0x1400f7f40  callers=865  size=4
    0x1400f70f0  callers=3980  size=288     0x140110140  callers=818  size=182

Four-byte bodies with a thousand callers are thunks and runtime helpers, not behaviour. Ranking by inbound references
selects the infrastructure every piece of code touches, which is exactly the code whose behaviour says nothing about
whether the app was replicated. A better witness set has to be selected by *app belonging*, not by fan-in.
"""

import io
import json
import sys
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
OUT = r"D:\projects\cyber-reverse\analysis\caller_ranking.tsv"
_id = [0]

SNIPPET = r"""
import idautils, ida_funcs, json
funcs = list(idautils.Functions())
lo, hi = __LO__, __HI__
out = []
for ea in funcs[lo:hi]:
    n = sum(1 for _ in idautils.XrefsTo(ea, 0))
    out.append([ea, n, ida_funcs.get_func_name(ea) or '', ida_funcs.get_func(ea).size() if ida_funcs.get_func(ea) else 0])
print('RANK', json.dumps(out))
"""


def rpc(method, params=None, timeout=180):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def call(tool, args, timeout=180):
    res = rpc("tools/call", {"name": tool, "arguments": args}, timeout=timeout)
    return json.loads(res["result"]["content"][0]["text"])


def main(argv):
    page = int(argv[0]) if argv else 2000
    max_pages = int(argv[1]) if len(argv) > 1 else 10**9
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "rank-callers", "version": "1"}})

    funcs = call("list_funcs", {"limit": 1}) if False else None   # count comes from the export instead
    total = 0
    with io.open(r"D:\projects\cyber-reverse\analysis\original_funcs.txt", encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and not line.startswith("#"):
                total += 1
    print("functions in the export: %d" % total)

    rows = []
    lo = 0
    pages = 0
    while lo < total and pages < max_pages:
        pages += 1
        code = SNIPPET.replace("__LO__", str(lo)).replace("__HI__", str(lo + page))
        res = call("py_eval", {"code": code}, timeout=300)
        out = res.get("stdout") or ""
        marker = out.find("RANK ")
        if marker < 0:
            print("  page %d: no RANK output; stderr=%r" % (lo, (res.get("stderr") or "")[:200]))
            break
        chunk = json.loads(out[marker + 5:].strip().splitlines()[0])
        rows.extend(chunk)
        print("  page [%d,%d) -> %d rows (running %d)" % (lo, lo + page, len(chunk), len(rows)))
        lo += page

    rows.sort(key=lambda r: -r[1])
    rows = [r[:4] for r in rows]
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("addr\tcallers\tname\tsize\n")
        for r in rows:
            fh.write("%x\t%d\t%s\t%d\n" % (r[0], r[1], r[2], r[3]))
    print()
    print("wrote %s (%d rows)" % (OUT, len(rows)))
    print("top 15 by caller count:")
    for r in rows[:15]:
        print("  0x%x  callers=%-4d size=%-6d %s" % (r[0], r[1], r[3], r[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
