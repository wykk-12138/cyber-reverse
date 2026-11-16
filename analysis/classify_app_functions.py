"""Classify the app-string function sample: UI wiring or business logic? (R721)

R720 selected 239 functions by "loads one of the app's own locale keys". Two decompiled samples both turned out to be
Avalonia property registration / binding setup rather than logic, which would mean the criterion selects UI wiring
instead of the behaviour C7c is about.

**Criterion, fixed before measuring**: sample the 400-1500 byte band (big enough to hold logic, small enough to read) and
classify each by its first callees:

    wiring   most callees are property/binding helpers (sub_1430xxxxx, sub_142E7xxxx, off_ globals of that family)
    logic    most callees do string/number/collection work, or the function has its own control flow

A sample where at least five of six are wiring rejects the criterion as a selector of business logic.
"""

import io
import json
import sys
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
_id = [0]

WIRING = ("sub_1430", "sub_142E7", "sub_142E8", "sub_142F", "sub_141BF")


def rpc(method, params=None, timeout=300):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def call(tool, args, timeout=300):
    res = rpc("tools/call", {"name": tool, "arguments": args}, timeout=timeout)
    return json.loads(res["result"]["content"][0]["text"])


def main(argv):
    addrs = argv or ["0x1405aaa60", "0x14061e0e0"]
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "classify", "version": "1"}})
    verdicts = []
    for a in addrs:
        r = call("decompile", {"addr": a, "max_lines": 400})
        code = r.get("code") or ""
        callees = set()
        for token in code.replace("(", " ").replace(")", " ").replace(",", " ").split():
            if token.startswith("sub_") or token.startswith("off_"):
                callees.add(token)
        wiring = sum(1 for c in callees if c.startswith(WIRING))
        total = len(callees) or 1
        share = 100.0 * wiring / total
        kinds = "wiring" if share >= 60 else "logic"
        verdicts.append(kinds)
        print("%-12s callees=%-3d wiring=%-3d (%4.0f%%) -> %s   lines=%d"
              % (a, total, wiring, share, kinds, len(code.splitlines())))
        sample = sorted(c for c in callees if not c.startswith(WIRING))[:4]
        if sample:
            print("             non-wiring callees: %s" % ", ".join(sample))
    print()
    print("verdicts: %s" % verdicts)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
