"""Extract the full GraphQL operation texts. (R788)

R787 left Warhammer with one hard gap: the replica speaks REST where the image speaks GraphQL. The operations are not
absent from the image -- they are literals in the pool, and a static initialiser at sub_140E4AE90 fills a global with
the endpoint plus two strings whose lengths it passes to an allocator. Searching the pool for lines beginning with
"mutation" returns them directly.

The point of writing them out is that they are the source of truth for the replica's requests: field names, argument
shapes and the response paths all live in this text, and reading it beats inferring it. The file is evidence, so it is
written to analysis/ rather than compiled into anything yet.

Why not an existing tool: str output truncates at the display layer and the strings are 800-2200 characters, so the
full text has to come from the plugin's own JSON, which is what this does.
"""

import io
import json
import subprocess
import sys

OUT = r"D:\projects\cyber-reverse\analysis\warhammer_graphql.txt"
PATTERNS = ["^mutation", "^query"]


def fetch(pattern):
    out = subprocess.run([sys.executable, r"D:\projects\cyber-reverse\analysis\ida.py", "str", pattern],
                         capture_output=True, text=True, cwd=r"D:\projects\cyber-reverse")
    i = out.stdout.find("{")
    if i < 0:
        return []
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except ValueError:
        return []
    return d.get("matches", [])


def main():
    rows = []
    seen = set()
    for pattern in PATTERNS:
        for m in fetch(pattern):
            text = m.get("string", "")
            # keep only operation bodies: they start with a GraphQL keyword and contain a selection set
            if "{" not in text or len(text) < 200:
                continue
            key = (m.get("addr"), text[:40])
            if key in seen:
                continue
            seen.add(key)
            rows.append((m.get("addr"), text))

    rows.sort(key=lambda r: r[0])
    body = ["# GraphQL operations recovered from the image (R788)", ""]
    for addr, text in rows:
        head = text.split("\n", 1)[0][:100]
        body.append("## %s  (%d chars)" % (addr, len(text)))
        body.append("# " + head)
        body.append("")
        body.append(text.rstrip())
        body.append("")
        body.append("---")
        body.append("")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(body))
    print("  wrote %d operations to %s" % (len(rows), OUT))
    for addr, text in rows:
        named = ""
        first = text.split("\n", 1)[0]
        if first.startswith("mutation ") or first.startswith("query "):
            named = first.split("(", 1)[0].split("{", 1)[0].strip()
        print("    %-14s %5d chars  %s" % (addr, len(text), named or "(anonymous)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
