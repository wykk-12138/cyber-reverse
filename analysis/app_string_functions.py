"""Select probe targets by app belonging: which functions reference the app's own locale keys? (R720)

**Why this exists** (project convention §1.2): R719 measured that ranking by caller count selects runtime glue --
four-byte field getters called 865 times. The replacement criterion is *app belonging*: a function that loads one of
this application's locale keys is app code by construction, because no other program contains that string.

`analysis/disp32_scan_any.py` already scans every byte of `.text` and matches a **set** of target addresses in one
numpy pass (R702 built it after the aligned-only variant gave a false zero). It is reused here rather than rewritten.

**Why now**: C7c needs behaviour witnesses, and this is the only criterion proposed so far whose selection is provable
from the binary rather than assumed from fan-in or from names.

**Criterion, fixed before measuring**:

  * `keys_located` -- locale keys whose literal IDA can find; fewer than the catalogue's count means the search is
    incomplete and the function count below is a floor, not a total.
  * `functions_hit` -- distinct functions containing a `lea` whose displacement resolves to one of those literals.
  * The result is only meaningful if `keys_located` is close to the catalogue size; otherwise this is reported as
    partial and the gap named.
"""

import io
import json
import os
import sys

import numpy as np

ROOT = r"D:\projects\cyber-reverse"
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import disp32_scan_any as D          # reuse the validated scanner rather than reimplementing it
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
LOCALES = os.path.join(ROOT, "replica", "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
OUT = os.path.join(ROOT, "analysis", "app_string_functions.tsv")
_id = [0]


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


LOCATE = r"""
import idautils, json, io
keys = set(json.load(io.open(__KEYS__, encoding='utf-8')))
found = {}
for s in idautils.Strings():
    t = str(s)
    if t in keys:
        found[t] = int(s.ea)
print('LOCATED', json.dumps(found))
"""

MAP_FUNCS = r"""
import ida_funcs, json
sites = [int(x, 16) for x in __SITES__]
out = {}
for ea in sites:
    f = ida_funcs.get_func(ea)
    if f:
        out['%x' % ea] = [f.start_ea, ida_funcs.get_func_name(f.start_ea) or '']
print('MAPPED', json.dumps(out))
"""


def main():
    keys = list(json.load(io.open(LOCALES, encoding="utf-8")).keys())
    print("locale keys in the catalogue: %d" % len(keys))

    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "app-strings", "version": "1"}})

    res = call("py_eval", {"code": LOCATE.replace("__KEYS__", repr(LOCALES.replace("\\", "/")))}, timeout=600)
    out = res.get("stdout") or ""
    i = out.find("LOCATED ")
    if i < 0:
        print("locate failed: %r" % (res.get("stderr") or out)[:400])
        return 1
    located = json.loads(out[i + 8:].strip().splitlines()[0])
    print("keys IDA could locate        : %d" % len(located))
    if not located:
        print("nothing to scan")
        return 1

    # the literal's characters start at s.ea; the frozen object header is 12 bytes earlier
    targets = {va - 12 for va in located.values()}
    data = open(D.BINARY, "rb").read()
    hits = D.scan(data, targets)
    total_sites = sum(len(v) for v in hits.values())
    print("lea sites resolving to them  : %d" % total_sites)

    sites = sorted({site for v in hits.values() for site in v})
    print("distinct sites               : %d" % len(sites))

    # map sites -> functions in one more py_eval, in chunks to stay inside the reply budget
    funcs = {}
    for lo in range(0, len(sites), 400):
        chunk = [hex(s + (D.TEXT_VA - D.TEXT_OFF)) for s in sites[lo:lo + 400]]
        r = call("py_eval", {"code": MAP_FUNCS.replace("__SITES__", repr(chunk))}, timeout=300)
        o = r.get("stdout") or ""
        j = o.find("MAPPED ")
        if j < 0:
            print("  map chunk at %d failed" % lo)
            continue
        for _site, (start, name) in json.loads(o[j + 7:].strip().splitlines()[0]).items():
            funcs[start] = name

    print("distinct functions           : %d" % len(funcs))
    print()
    print("criterion check: keys_located %d / %d (%.1f%% of the catalogue)"
          % (len(located), len(keys), 100.0 * len(located) / len(keys)))

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# functions that load an app locale key (R720)\n")
        fh.write("func_addr\tfunc_name\n")
        for start, name in sorted(funcs.items()):
            fh.write("%x\t%s\n" % (start, name))
    print("wrote %s (%d functions)" % (OUT, len(funcs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
