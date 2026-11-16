"""Query xrefs for a string at BOTH candidate addresses: the character data and the object header. (R703)

**Why this exists** (project convention §1.2): `analysis/ida.py xrefs` asks IDA about one address, and `ida.py str`
answers with the address of a literal's CHARACTER data. That pairing is wrong for .NET NativeAOT: a frozen string is an
object laid out `[MethodTable:8][length:4][chars...]`, and compiled code `lea`s the OBJECT, not the chars.

R691 queried the chars address, got zero, and concluded "this binary has no reference to its strings". The reference was
there the whole time, 12 bytes earlier:

    xrefs 0x146E4D160 (object) -> 1, site 0x140F7739B in sub_140F77350
    xrefs 0x146E4D16C (chars)  -> 0

Five different probes were run at R691 and all five inherited that same wrong address, which made their agreement look
like corroboration. **Independence is a property of the error, not of the tool.** So the fix is not another probe -- it is
one helper that tries both addresses by default, so nobody has to know about the 12 bytes.

Usage:
    python analysis/xref_both.py 0x146E4D1C4            # a chars address from `ida.py str`
    python analysis/xref_both.py --text "ProfileCsv.Error.UnknownState"
"""

import json
import sys
import urllib.request

URL = "http://127.0.0.1:13337/mcp"
HEADER_OFFSET = 12   # [MethodTable:8][length:4] precedes the characters
_id = [0]


def rpc(method, params=None, timeout=180):
    _id[0] += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def call(tool, args, timeout=180):
    res = rpc("tools/call", {"name": tool, "arguments": args}, timeout=timeout)
    text = res["result"]["content"][0]["text"]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv):
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "xref-both", "version": "1"}})

    if argv and argv[0] == "--text":
        needle = argv[1]
        found = call("find_regex", {"pattern": needle, "limit": 8})
        addrs = []
        for row in (found.get("matches") or found.get("results") or []):
            a = row.get("addr") or row.get("address")
            if a:
                addrs.append(int(a, 16))
        if not addrs:
            print("no literal matched %r" % needle)
            return 1
    elif argv:
        addrs = [int(argv[0], 16)]
    else:
        print(__doc__)
        return 2

    for chars in addrs:
        obj = chars - HEADER_OFFSET
        print("literal chars 0x%X   object header 0x%X" % (chars, obj))
        for label, addr in (("chars ", chars), ("object", obj)):
            res = call("xrefs_to", {"addrs": [hex(addr)]})
            hits = []
            if isinstance(res, list):
                for item in res:
                    hits.extend(item.get("xrefs") or [])
            elif isinstance(res, dict):
                hits.extend(res.get("xrefs") or [])
            fns = sorted({(h.get("fn") or {}).get("name", "?") for h in hits})
            print("  %s 0x%X -> %d xref(s) %s" % (label, addr, len(hits), fns if fns else ""))
            for h in hits[:6]:
                fn = (h.get("fn") or {})
                print("      site 0x%s in %s" % (h.get("addr"), fn.get("name", "?")))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
