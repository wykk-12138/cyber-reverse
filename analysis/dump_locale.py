# Print locale entries whose key matches a regex.
# Usage: python dump_locale.py <lang> <key-regex>
import io, json, re, sys

lang = sys.argv[1] if len(sys.argv) > 1 else "en"
pat = sys.argv[2] if len(sys.argv) > 2 else "."
path = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Core\Locales\Cybersole.Locales.%s.json" % lang
data = json.loads(io.open(path, encoding="utf-8-sig").read())
rx = re.compile(pat, re.I)


def walk(node, prefix=""):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, prefix + k + "." if prefix or True else k)
    elif isinstance(node, str):
        key = prefix[:-1]
        if rx.search(key):
            print("%s = %r" % (key, node))


walk(data)
