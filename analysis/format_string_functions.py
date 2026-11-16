"""Among the app-string functions, which reference a FORMAT string rather than a property name? (R721b)

R721's finding: the 239 app-string functions are dominated by UI state-refresh code, whose behaviour is "set property P
of object O", and property identity is blocked (R715 showed accessor and descriptor names are not type-attributable).
Probing those would need the property name to be attributable.

**A different signal, testable directly**: a function that loads a string containing `{0}` / `{1}` formats a message.
Its behaviour is an output string, which can be asserted without knowing any type: give it the arguments, compare the
text.

**Criterion, fixed before measuring**: a function qualifies when one of the locale literals it loads contains a
replacement placeholder. Report the count and the strings, because the strings themselves are the evidence.
"""

import io
import json
import os
import sys

ROOT = r"D:\projects\cyber-reverse"
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
LOCALES = os.path.join(ROOT, "replica", "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
OUT = os.path.join(ROOT, "analysis", "format_string_functions.tsv")
_id = [0]

SNIPPET = r"""
import idautils, ida_funcs, json, io
keys = json.load(io.open(__KEYS__, encoding='utf-8'))
fmt = {k: v for k, v in keys.items() if '{' in v}
out = []
targets = {v: k for k, v in fmt.items()}
for s in idautils.Strings():
    t = str(s)
    if t in targets:
        out.append([int(s.ea), targets[t], t])
print('FMT', json.dumps(out))
"""


def rpc(method, params=None, timeout=300):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    keys = json.load(io.open(LOCALES, encoding="utf-8"))
    fmt_keys = {k: v for k, v in keys.items() if "{" in v}
    print("locale entries whose text carries a placeholder: %d of %d" % (len(fmt_keys), len(keys)))

    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "fmt", "version": "1"}})
    res = rpc("tools/call", {"name": "py_eval",
                             "arguments": {"code": SNIPPET.replace("__KEYS__", repr(LOCALES.replace("\\", "/")))}},
              timeout=600)
    out = json.loads(res["result"]["content"][0]["text"]).get("stdout") or ""
    i = out.find("FMT ")
    if i < 0:
        print("locate failed: %r" % out[:300])
        return 1
    rows = json.loads(out[i + 4:].strip().splitlines()[0])
    print("format-string literals located: %d" % len(rows))
    for ea, key, text in rows[:12]:
        print("  0x%x  %-46s %r" % (ea, key, text[:60]))
    if not rows:
        return 0

    targets = {ea - 12 for ea, _k, _t in rows}
    import disp32_scan_any as D
    data = open(D.BINARY, "rb").read()
    hits = D.scan(data, targets)
    sites = sorted({s for v in hits.values() for s in v})
    print()
    print("lea sites resolving to a format string: %d" % len(sites))

    MAP = r"""
import ida_funcs, json
out = {}
for ea in __SITES__:
    f = ida_funcs.get_func(ea)
    if f: out['%x' % ea] = [f.start_ea, ida_funcs.get_func_name(f.start_ea) or '']
print('MAPPED', json.dumps(out))
"""
    funcs = {}
    site_va = [hex(s + (D.TEXT_VA - D.TEXT_OFF)) for s in sites]
    for lo in range(0, len(site_va), 400):
        r = rpc("tools/call", {"name": "py_eval",
                               "arguments": {"code": MAP.replace("__SITES__", repr(site_va[lo:lo + 400]))}},
                timeout=300)
        o = json.loads(r["result"]["content"][0]["text"]).get("stdout") or ""
        j = o.find("MAPPED ")
        if j >= 0:
            for _s, (start, name) in json.loads(o[j + 7:].strip().splitlines()[0]).items():
                funcs[start] = name

    print("distinct functions formatting a message: %d" % len(funcs))
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("func_addr\tfunc_name\n")
        for start, name in sorted(funcs.items()):
            fh.write("%x\t%s\n" % (start, name))
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
