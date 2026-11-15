# R70 cross-check: find the code that references a locale key literal, then decompile it.
# The locale JSON blobs live in .rdata as data; the *code* also holds the key strings, and those
# are the ones with code xrefs. This walks: find_regex -> pick the non-.rdata hit -> xrefs_to.
import io, json, os, re, sys, urllib.request

URL = "http://127.0.0.1:13337/mcp"
KEY = sys.argv[1] if len(sys.argv) > 1 else "Accounts.Context.CopyMany"


def rpc(tool, args):
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read().decode("utf-8"))


def text_of(result):
    content = result.get("result", {}).get("content", [])
    return "".join(c.get("text", "") for c in content if c.get("type") == "text")


found = json.loads(text_of(rpc("find_regex", {"pattern": re.escape(KEY), "limit": 12})))
hits = found.get("matches", [])
print("matches=%d" % len(hits))
for m in hits:
    print("  %s  len=%d  %r" % (m["addr"], len(m["string"]), m["string"][:70]))

# The blobs are huge; the code-side literals are short.
short = [m for m in hits if len(m["string"]) <= 200]
print("short_hits=%d" % len(short))
if not short:
    raise SystemExit("no short literal to xref")

target = short[-1]["addr"]
print("xref target=%s" % target)
xr = json.loads(text_of(rpc("xrefs_to", {"addrs": [target]})))
print(json.dumps(xr, indent=2)[:4000])
