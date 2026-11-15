import io, json, subprocess, sys

QUERIES = [
    ("Nike endpoints", "api\\.nike\\.com"),
    ("Nike identifiers", "nike-[a-z-]+|NIKE-[A-Z]+|Nike-Kasada-Version"),
    ("Nike markets", "Nike [A-Z]{2}$"),
    ("checkout fragment", "checkouts/c?/"),
    ("identification signature", "IdentificationSignature"),
]

args = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\args_audit.json"
rows = []

for label, pattern in QUERIES:
    io.open(args, "w", encoding="utf-8").write(
        json.dumps({"pattern": pattern, "limit": 300}))
    out = subprocess.run([sys.executable, "ida_mcp.py", "call", "find_regex", "@" + args],
                         capture_output=True, text=True, cwd=r"C:\Users\wykk\AppData\Local\Cybersole\analysis")
    text = out.stdout or out.stderr
    try:
        data = json.loads(text)
        # the plugin sometimes wraps the payload in a list
        if isinstance(data, list):
            data = data[0]
        n = data.get("n")
        done = (data.get("cursor") or {}).get("done")
        rows.append((label, pattern, n, done))
    except Exception as ex:
        rows.append((label, pattern, "ERR: " + text[:80], None))

for label, pattern, n, done in rows:
    print("%-24s %-46s n=%-4s done=%s" % (label, pattern, n, done))
