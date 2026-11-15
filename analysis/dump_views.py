# Dump the Avalonia XAML resource index + embedded locale blob out of the binary.
#
# The whole ClassToResourcePathIndex and the locale JSON live as ONE string literal, so a single
# find_regex hit carries both. Address seen: 0x143c4c523 (re-resolved here, not hard-coded).
import io, json, os, re, sys, urllib.request

URL = "http://127.0.0.1:13337/mcp"
OUT = os.path.dirname(os.path.abspath(__file__))


def rpc(tool, args):
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode("utf-8"))


def text_of(result):
    content = result.get("result", {}).get("content", [])
    return "".join(c.get("text", "") for c in content if c.get("type") == "text")


raw = text_of(rpc("find_regex", {"pattern": "ClassToResourcePathIndex", "limit": 3}))
data = json.loads(raw)
blob = data["matches"][0]["string"] if data.get("matches") else ""

io.open(os.path.join(OUT, "avalonia_resources.txt"), "w", encoding="utf-8", newline="\n").write(blob)
print("blob_chars=%d addr=%s" % (len(blob), data["matches"][0]["addr"] if data.get("matches") else "-"))

views = re.findall(r"<a:Key>([^<]+)</a:Key><a:Value>(/[^<]+\.axaml)</a:Value>", blob)
print("views=%d" % len(views))
with io.open(os.path.join(OUT, "original_views.txt"), "w", encoding="utf-8", newline="\n") as fh:
    for cls, path in views:
        fh.write("%s\t%s\n" % (cls, path))

for cls, path in views:
    if ".Accounts" in cls:
        print("  %s -> %s" % (cls, path))
