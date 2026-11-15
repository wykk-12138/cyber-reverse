# Read the big Avalonia resource blob at a known address and split it into
#   avalonia_resources.txt  (raw)
#   original_views.txt      (Class<TAB>axaml path)
#   embedded_locale.json    (the locale literal that trails the XML)
import io, json, os, re, urllib.request

URL = "http://127.0.0.1:13337/mcp"
OUT = os.path.dirname(os.path.abspath(__file__))
ADDR = os.environ.get("BLOB_ADDR", "0x143c4c523")


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


raw = text_of(rpc("find_regex", {"pattern": "ACCOUNTS SELECTED", "limit": 5}))
try:
    data = json.loads(raw)
except Exception:
    print("RAW:", raw[:600])
    raise
# The locale JSON and the XAML index are one string literal, so the hit we want is the longest.
blob = max((m.get("string", "") for m in data.get("matches", [])), key=len, default="")
print("blob_chars=%d" % len(blob))
io.open(os.path.join(OUT, "avalonia_resources.txt"), "w", encoding="utf-8", newline="\n").write(blob)

views = re.findall(r"<a:Key>([^<]+)</a:Key><a:Value>(/[^<]+\.axaml)</a:Value>", blob)
print("views=%d" % len(views))
with io.open(os.path.join(OUT, "original_views.txt"), "w", encoding="utf-8", newline="\n") as fh:
    for cls, path in views:
        fh.write("%s\t%s\n" % (cls, path))

# The locale JSON starts right after the closing XML tag.
cut = blob.find("</AvaloniaResourceXamlInfo>")
locale_text = blob[cut + len("</AvaloniaResourceXamlInfo>"):] if cut >= 0 else ""
print("locale_chars=%d" % len(locale_text))
if locale_text.strip().startswith("{"):
    io.open(os.path.join(OUT, "embedded_locale.json"), "w", encoding="utf-8", newline="\n").write(locale_text)
    try:
        keys = []

        def walk(node, prefix):
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, prefix + k + ".")
            elif isinstance(node, str):
                keys.append(prefix[:-1])

        walk(json.loads(locale_text), "")
        print("locale_keys=%d" % len(keys))
    except Exception as exc:
        print("locale json not parseable: %s" % exc)

for cls, path in views:
    if "Accounts" in cls:
        print("  %s -> %s" % (cls, path))
